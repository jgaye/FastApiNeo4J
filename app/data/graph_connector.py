from typing import Optional, Tuple

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from app.config import settings
from app.schemas.input import PersonInput, ChildInput, FriendInput


class PersonNotFound(Exception):
    def __init__(self, name: str):
        self.message = f"The person name {name} was not found."


class GraphConnector:

    def __init__(self):
        with GraphDatabase.driver(settings.neo4j_uri) as driver:
            try:
                driver.verify_connectivity()
            except ServiceUnavailable:
                raise ServiceUnavailable(
                    f"The Neo4J db instance was not found at {settings.neo4j_uri}, stopping the API service."
                )
            self.driver = driver
            self.database = settings.neo4j_database

    def run_query(self, query: str, parameters: Optional[dict] = None) -> list[dict]:
        records, summary, keys = self.driver.execute_query(
            query,  # Type issue as I don't know how to confirm it's a LiteralString
            parameters,
            database_=self.database,
        )
        return [record.data() for record in records]

    def fetch_friends_parents_children(
        self, name: str
    ) -> Tuple[list[dict], list[dict], list[dict]]:
        friends_records = self.run_query(
            """
        MATCH(person: Person {name: $name})-[r: ARE_FRIENDS]-(friend:Person)
        RETURN friend.name
        """,
            {"name": name},
        )
        parents_records = self.run_query(
            """
        MATCH(parent: Person)-[r: PARENT]->(child:Person {name: $name}) 
        RETURN parent.name
        """,
            {"name": name},
        )
        children_records = self.run_query(
            """
        MATCH(parent: Person {name: $name})-[r: PARENT]->(child:Person)
        RETURN child.name
        """,
            {"name": name},
        )

        return friends_records, parents_records, children_records

    def unpack_person(self, packed_person: dict) -> dict:
        friends, parents, children = self.fetch_friends_parents_children(
            packed_person["name"]
        )

        packed_person["parent_of"] = [
            {"name": child["child.name"]} for child in children
        ]
        packed_person["child_of"] = [
            {"name": parent["parent.name"]} for parent in parents
        ]
        packed_person["friends_with"] = [
            {"name": friend["friend.name"]} for friend in friends
        ]

        return packed_person

    def reset_db(self) -> None:
        self.driver.execute_query(
            "MATCH (n) DETACH DELETE n",
            database_=self.database,
        )

        # It's better practice to run large managed transactions at the session level to indicate that I trust the query
        # If I were to use driver.execute_query here, a warning that the query is insecure would pop (typing)
        def do_write_init_script(tx):
            with open("app/helpers/init_neo4j.txt", "r") as init_script:
                result = tx.run("".join(init_script.readlines()))
            return list(result)

        with self.driver.session() as session:
            session.execute_write(do_write_init_script)

    def list_people(self) -> list[dict]:
        people_records = self.run_query("MATCH (person:Person) RETURN person")
        people = [self.unpack_person(record["person"]) for record in people_records]
        return people

    def fetch_person(self, name: str) -> dict:
        person_records = self.run_query(
            "MATCH (person:Person {name: $name}) RETURN person",
            parameters={"name": name},
        )
        if not person_records:
            raise PersonNotFound(name)
        return self.unpack_person(person_records[0]["person"])

    def fetch_person_ancestors(self, name: str) -> list[dict]:
        ancestors_records = self.run_query(
            "MATCH(person: Person)-[r: PARENT *1..]->(child:Person {name: $name}) RETURN person",  # recursively find the parents
            parameters={"name": name},
        )
        people = [self.unpack_person(record["person"]) for record in ancestors_records]
        return people

    def fetch_person_family_friends(self, name: str) -> list[dict]:
        # This query finds all UNIQUE persons that are friends (depth 1) with any family members
        # UNION the friends of the original person (as they are in their own family)
        family_friend_records = self.run_query(
            """
            MATCH(person: Person {name: $name})-[kin: PARENT *1..]-(family_member:Person)-[friendship:ARE_FRIENDS]-(family_friend: Person) 
                RETURN family_friend as person
            UNION 
                MATCH(person: Person {name: $name})-[friendship:ARE_FRIENDS]-(family_friend: Person) 
                RETURN family_friend as person
            """,
            parameters={"name": name},
        )
        people = [
            self.unpack_person(record["person"]) for record in family_friend_records
        ]
        return people

    def create_person(self, person_info: PersonInput) -> dict:
        person_records = self.run_query(
            "CREATE (person:Person {name:$name , nickname:$nickname }) RETURN person",
            parameters={"name": person_info.name, "nickname": person_info.nickname},
        )
        return self.unpack_person(person_records[0]["person"])

    def update_person(self, name: str, person_info: PersonInput) -> dict:
        person_records = self.run_query(
            """
            MATCH(person:Person {name: $name})
            SET person = {name:$new_name, nickname:$new_nickname}
            RETURN person
            """,
            parameters={
                "name": name,
                "new_name": person_info.name,
                "new_nickname": person_info.nickname,
            },
        )
        if not person_records:
            raise PersonNotFound(name)
        return self.unpack_person(person_records[0]["person"])

    def remove_person(self, name: str) -> None:
        # DETACH makes the equivalent to
        # MATCH(person:Person {name: $name})-[kinship:PARENT]-(parent:Person)
        # MATCH(person:Person {name: $name})-[friendship:ARE_FRIENDS]-(friend:Person)
        # DELETE kinship, friendship, person
        self.run_query(
            """
            MATCH(person:Person {name: $name})
            DETACH DELETE person
            """,
            parameters={"name": name},
        )

    def create_child_relationship(
        self, parent_name: str, child_info: ChildInput
    ) -> dict:
        person_records = self.run_query(
            """
            MATCH (parent:Person {name:$parent_name}) 
            MATCH (child:Person {name:$child_name})
            CREATE (parent)-[:PARENT]->(child)
            RETURN parent as person
            """,
            parameters={
                "parent_name": parent_name,
                "child_name": child_info.child_name,
            },
        )
        if not person_records:
            raise PersonNotFound(parent_name)
        return self.unpack_person(person_records[0]["person"])

    def remove_child_relationship(self, parent_name: str, child_name: str) -> None:
        self.run_query(
            """
            MATCH(parent:Person {name: $parent_name})-[r:PARENT]->(child:Person {name: $child_name}) 
            DELETE r
            """,
            parameters={"parent_name": parent_name, "child_name": child_name},
        )

    def create_friend_relationship(
        self, originator_name: str, friend_info: FriendInput
    ) -> dict:
        person_records = self.run_query(
            """
            MATCH (originator:Person {name:$originator_name}) 
            MATCH (friend:Person {name:$friend_name})
            CREATE (originator)-[:ARE_FRIENDS]->(friend)
            RETURN originator as person
            """,
            parameters={
                "originator_name": originator_name,
                "friend_name": friend_info.friend_name,
            },
        )
        if not person_records:
            raise PersonNotFound(originator_name)
        return self.unpack_person(person_records[0]["person"])

    def remove_friend_relationship(self, name: str, friend_name: str) -> None:
        self.run_query(
            """
            MATCH(person:Person {name: $name})-[r:ARE_FRIENDS]-(friend:Person {name: $friend_name}) 
            DELETE r
            """,
            parameters={"name": name, "friend_name": friend_name},
        )

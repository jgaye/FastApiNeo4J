import yaml

with open("app/data/data.yml", "r") as stream:
    people = yaml.safe_load(stream)

with open("helpers/init_neo4j.txt", "w") as file:
    for person in people["people"]:
        nickname_section = ""
        if "nickname" in person and person["nickname"]:
            nickname_section = f", nickname:'{person['nickname']}'"
        file.write(
            f"CREATE ({person['firstname']}:Person {{name:'{person['firstname']} {person['lastname']}' {nickname_section} }})\n"
        )

    for person in people["people"]:
        if "parent_of" in person and person["parent_of"]:
            for child in person["parent_of"]:
                file.write(
                    f"CREATE ({person['firstname']})-[:PARENT]->({child.split(' ')[0]})\n"
                )

    # Henry Brown has 10 friends
    friendships = """
CREATE (Henry)-[:ARE_FRIENDS]->(Ian)
CREATE (Henry)-[:ARE_FRIENDS]->(George)
CREATE (Henry)-[:ARE_FRIENDS]->(Ruby)
CREATE (Henry)-[:ARE_FRIENDS]->(John)
CREATE (Henry)-[:ARE_FRIENDS]->(Susan)
CREATE (Henry)-[:ARE_FRIENDS]->(Rebecca)
CREATE (Henry)-[:ARE_FRIENDS]->(Mia)
CREATE (Henry)-[:ARE_FRIENDS]->(Luke)
CREATE (Henry)-[:ARE_FRIENDS]->(Anna)
CREATE (Henry)-[:ARE_FRIENDS]->(Frank)
"""
    # David White and Liam Wilson are friends
    friendships += "CREATE (David)-[:ARE_FRIENDS]->(Liam)\n"

    # Jessica Wilson and Victor Smith are friends
    friendships += "CREATE (Jessica)-[:ARE_FRIENDS]->(Victor)\n"

    # Lisa Smith and Mike Brown are friends
    friendships += "CREATE (Lisa)-[:ARE_FRIENDS]->(Mike)\n"

    # no friends for the Taylors

    file.write(friendships)

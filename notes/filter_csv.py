import csv

def filter_csv(input_file, output_file, card_names):
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row['Name'] in card_names:
                writer.writerow(row)

# List of card names to keep
card_names_to_keep = [
    'Thornspire Verge', 'Peer Past the Veil', 'Doomsday Excruciator', 'Marvin, Murderous Mimic',
    'Kona, Rescue Beastie', 'Ghost Vacuum', 'The Swarmweaver', 'The Mindskinner',
    'Winter, Misanthropic Guide', "Victor, Valgavoth's Seneschal", 'Rip, Spawn Hunter',
    'Nashi, Searcher in the Dark', 'Marina Vendrell', 'Zimone, All-Questioning',
    'The Wandering Rescuer', 'Forest', 'Mountain', 'Tyvar, the Pummeler',
    'Kianne, Corrupted Memory', 'The Master of Keys', 'Zimone, Mystery Unraveler',
    'Valgavoth, Harrower of Souls', 'Twitching Doll', "Valgavoth's Onslaught",
    'Charred Foyer // Warped Space', 'Gloomlake Verge', 'Leyline of the Void',
    'Enduring Tenacity', 'Mirror Room // Fractured Realm', "Valgavoth's Lair",
    'Valgavoth, Terror Eater', 'Overlord of the Hauntwoods', 'Cursed Recording',
    'Plains', 'Swamp', 'Terramorphic Expanse', 'Island', 'Under the Skin',
    'Withering Torment', "Marina Vendrell's Grimoire"
]

# Filter the CSV
filter_csv('new_items.csv', 'filtered_new_items.csv', card_names_to_keep)

print("Filtered CSV file has been created: filtered_new_items.csv")
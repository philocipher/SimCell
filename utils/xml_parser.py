# utils/parser.py
 

import xml.etree.ElementTree as ET

def parse_emission_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    trajectory_dict = {}

    for timestep in root.iter('timestep'):
        time = float(timestep.attrib['time'])
        for vehicle in timestep.iter('vehicle'):
            vehicle_id = vehicle.attrib['id']
            x = float(vehicle.attrib['x'])
            y = float(vehicle.attrib['y'])

            if vehicle_id not in trajectory_dict:
                trajectory_dict[vehicle_id] = {'time': [], 'x': [], 'y': []}

            trajectory_dict[vehicle_id]['time'].append(time)
            trajectory_dict[vehicle_id]['x'].append(x)
            trajectory_dict[vehicle_id]['y'].append(y)

    return trajectory_dict
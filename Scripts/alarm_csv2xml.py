#!/usr/bin/env python
# coding: utf-8
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

import click


def csvtoxml(infile, outfile, cname):
    """ convert CSV to XML suitable for Phoebus """
    config = ET.Element('config')
    config.set('name', cname)

    with open(infile, 'r', encoding='utf-8-sig') as fh:
        content = csv.DictReader(fh, escapechar='\\')
        stack = []
        stack.append(config)
        level = 0
        for row in content:
            row.update((k, v.strip()) for k, v in row.items())
            if row['#Indent']:
                level = int(row['#Indent'])
                while len(stack) > level + 1:
                    stack.pop()
                sel = ET.SubElement(stack[level], 'component')
                sel.set('name', row['Branch'])
                stack.append(sel)
            else:
                pv = ET.SubElement(stack[-1], 'pv')
                pv.set('name', row['PV'])
                desc = ET.SubElement(pv, 'description')
                desc.text = row['Description']
                latch = ET.SubElement(pv, 'latching')
                latch.text = row['Latch'].capitalize() if row['Latch'] else "True"
                delay = ET.SubElement(pv, 'delay')
                delay.text = row['Delay']
                if 'Filter' in row and row['Filter']:
                    filter = ET.SubElement(pv, 'filter')
                    filter.text = row['Filter']
                if 'Guidance' in row and row['Guidance']:
                    guidance = ET.SubElement(pv, 'guidance')
                    guidance.text = row['Guidance']

        xm = minidom.parseString(ET.tostring(config, encoding='utf-8',
                                             xml_declaration=True,
                                             short_empty_elements=True))
    if outfile is None:
        outfile = infile.rsplit('.', 1)[0] + '.xml'
    with open(outfile, 'w', encoding='utf-8') as out:
        out.write(xm.toprettyxml(indent=" "*3))
    click.echo(f'Conversion of {infile} complete. See {outfile}')


@click.command()
@click.option('-i', '--infile', prompt='specify name of csv file', required=True,
            type=str, help='Name of CSV input file.')
@click.option('-o', '--outfile', default=None, required=False, type=str,
            help='Name of the XML output file. Derived from name of infile if unspecified.')
@click.option('-c', '--cname', prompt='specify name of the config', required=True,
            type=str, help='Name of the config to set inside the XML.')
def main_command(infile, outfile, cname):
    csvtoxml(infile, outfile, cname)

if __name__ == '__main__':
    main_command()


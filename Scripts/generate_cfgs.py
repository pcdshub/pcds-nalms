import re
from string import ascii_uppercase


def exptocfg(cname, expression_rows):
    with open(f'CFG/ioc-nalms-{cname}.cfg', 'w+') as cfg:
        # write all the boilerplate ioc stuff here
        cfg.write('RELEASE=/cds/group/pcds/epics/ioc/common/nalms/R1.0.0\n\n')
        for row in expression_rows:
            # default to empty string instead of None for formatting
            expression = {
                'PV': row['PV'],
                'Expression': row['Expression'],
                'LOLO': row.get('LOLO', ''),
                'LLSV': row.get('LLSV', ''),
                'LOW': row.get('LOW', ''),
                'LSV': row.get('LSV', ''),
                'HIGH': row.get('HIGH', ''),
                'HSV': row.get('HSV', ''),
                'HIHI': row.get('HIHI', ''),
                'HHSV': row.get('HHSV', ''),
            }
            # assume binary condition if no limits
            if not any(
                (
                    expression['LOLO'],
                    expression['LOW'],
                    expression['HIGH'],
                    expression['HIHI'],
                )
            ):
                # doesn't make sense to use low severity for binary condition
                if expression['HHSV']:
                    expression['HIHI'] = 1
                elif expression['HSV']:
                    expression['HIGH'] = 1
                else:
                    expression['HIGH'] = 1
                    expression['HSV'] = 'MAJOR'

            # should I fail if no alarm limits/severities are defined?
            # should I modify the pvname to ensure it's unique?
            # getting all pvs according to legal characters in epics
            # https://docs.epics-controls.org/en/latest/appdevguide/databaseDefinition.html#unquoted-strings
            pvs = re.findall(
                r'[a-zA-Z0-9_\-:.\[\]<>;]+:[a-zA-Z0-9_\-:.\[\]<>;]+',
                expression['Expression'],
            )
            num_pvs = len(pvs)
            if num_pvs == 0:
                # why would you use this without any pvs??
                pass
            elif num_pvs > 12:
                # too many
                pass

            index = -1

            # replacing each pv with A, B, C, ...
            def get_field(match):
                nonlocal index
                index = index + 1
                return ascii_uppercase[index]

            # padding for format
            pvs = pvs + [""] * (12 - len(pvs))
            re.sub(
                expression['Expression'],
                get_field,
                r'[a-zA-Z0-9_\-:.\[\]<>;]+:[a-zA-Z0-9_\-:.\[\]<>;]+',
            )
            # instantiation for ioc
            cfg.write(
                'CMP(PV={},EXPR={},LOLO={},LLSV={},LOW={},LSV={},'
                'HIGH={},HSV={},HIHI={},HHSV={},A={},B={},C={},D={},'
                'E={},F={},G={},H={},I={},J={},K={},L={})\n'.format(
                    *expression.values(), *pvs
                )
            )

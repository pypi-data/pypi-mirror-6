def haab_to_nature(num, day, year):
    haab = { 'pop': 1, 'no': 2, 'zip': 3, 'zotz': 4, 'tzec': 5, \
             'xul': 6, 'yoxkin': 7, 'mol': 8, 'chen': 9, 'yax': 10, \
             'zac': 11, 'ceh': 12, 'mac': 13, 'kankin': 14, \
             'muan': 15, 'pax': 16, 'koyab': 17, 'cumhu': 18 }
    if day == 'cumhu':
        if int(num) > 4:
            print "the data is not correct!"
        else:
            days = int(num) + 1 + 18 * 20 + int(year) * 365
    else:
        days = int(num) + 1 + ( haab[day] - 1 ) * 20 + int(year) * 365
    return days

def nature_to_tzolkin(days):
    t_year = int(days) / 260
    tzolkin = [ 'imix', 'ik', 'akbal', 'kan', 'chicchan', 'cimi', \
                'manik', 'lamat', 'muluk', 'ok', 'chuen', 'eb', \
                'ben', 'ix', 'mem', 'cib', 'caban', 'eznab', \
                'canac', 'ahau' ]
    t_days = int(days) % 260
    t_num = t_days % 13
    t_day = tzolkin[t_days % 20 - 1 ]
    return str(t_num) + " " + str(t_day) + " " + str(t_year)

if __name__=='__main__':


    for line in open('poj1008.txt'):
        line = line.strip('\n').replace('.', '').split(' ')
        print nature_to_tzolkin(haab_to_nature(line[0], line[1], line[2]))
    


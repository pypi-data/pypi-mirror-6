from django.conf import settings
import datetime

def get_backend(backend_name=None):
    if not backend_name:
        backend_name = settings.HOMEBANKING_BACKEND
    mod = __import__('homebanking.drivers.%s' % (backend_name,),
                     globals(), locals())
    return getattr(mod.drivers, backend_name).backend_class

def latin1_csv_reader(f):
    for row in csv.reader(f, delimiter=';', quotechar='"'):
        yield [cell.decode('latin1') for cell in row]

def parse_date(s):
    return datetime.datetime.strptime(s, '%d-%m-%Y')

def parse_amount(s):
    return float(s.replace('.', '').replace(',', '.'))

def months_of_interest():
    day = datetime.date.today()
    def format_month(dt):
        return dt.strftime('%Y-%m')
    retval = [format_month(day)]
    months_left = 2
    while months_left > 0:
        day = day.replace(day=1)
        day -= datetime.timedelta(days=1)
        retval += [format_month(day)]
        months_left -= 1
    return retval


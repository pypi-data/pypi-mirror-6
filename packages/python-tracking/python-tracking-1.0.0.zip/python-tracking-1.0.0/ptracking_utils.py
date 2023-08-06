__author__ = 'Diego Garcia'

import urllib.request as req
import re


class PyTrackingUtils:
    @staticmethod
    def get_html(url):
        page = req.urlopen(url)
        return page.read().decode("ISO-8859-1")

    @staticmethod
    def clean_up_string(s):
        return re.sub('\W+', ' ', s, re.DOTALL).strip()


class PyTrackingBR:

    @staticmethod
    def get_tracking(cod):
        data = []
        s = PyTrackingUtils.get_html('http://websro.correios.com.br/sro_bin/txect01$.QueryList?P_ITEMCODE=&P_LINGUA=001&P_TESTE=&P_TIPO=001&P_COD_UNI={}&Z_ACTION=Search'.format(cod))
        p_re = r'rowspan=\d+>(?P<time>[^<]+)</td><td>(?P<location>[^<]+)</td><td><FONT COLOR="[A-F\d]{6}">(?P<status>[^<]+)|colspan=\d+>(?P<observation>[^<]+?)</'
        for m in re.finditer(p_re, s, re.DOTALL + re.UNICODE):
            if m.group('time') is not None:
                data.append({"time": m.group('time'), "location": m.group('location'), "status": m.group('status')})
            else:
                data[-1]["observation"] = m.group('observation')
        return data


class PyTrackingUSPS:

    @staticmethod
    def get_tracking(cod):
        data = []
        s = PyTrackingUtils.get_html('http://www.stamps.com/shipstatus/submit/?confirmation={}'.format(cod))
        p_re = r'(?s)class="scanHistoryLeftCol">(?P<time>[^<]*).*?<td>(?P<time_detail>[^<]*).*?<td>(?P<location>[^<]*).*?ol">(?P<status>[^<]*)'
        obs = ""
        for m in re.finditer(p_re, s, re.DOTALL):
            if m.group('location').strip() != "":
                data.append({"time": '{}, {}'.format(m.group('time'), m.group('time_detail')), "location": PyTrackingUtils.clean_up_string(m.group('location')), "status": m.group('status')})
                if obs != "":
                    data[-1]["observation"] = obs
                    obs = ""
            else:
                obs = m.group('status')
        return data
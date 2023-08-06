
class ASPXSession:
    """
    Holds ASPX session variables, which are used for form validation between pages.
    """
    def __init__(self, html):
        """
        Takes HTML page and uses XPath to find session variables.
        """
        try:
            self.viewstate = html.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
            self.eventvalidation = html.xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]
        except:
            raise Exception("Couldn't build ASPX session: viewstate/eventvalidation fields not found in HTML")

    def parameters(self):
        return {
            '__VIEWSTATE': self.viewstate,
            '__EVENTVALIDATION': self.eventvalidation,
        }

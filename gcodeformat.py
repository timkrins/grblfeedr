import sys
import re

class GForm():
    def formatx(self,m):
        return("<x>"+m.group(0)+"</x>")
        
    def formaty(self,m):
        return("<y>"+m.group(0)+"</y>")
        
    def formatz(self,m):
        return("<z>"+m.group(0)+"</z>")
        
    def formatg01(self,m):
        return("<g01>"+m.group(0)+"</g01>")
        
    def formatg00(self,m):
        return("<g00>"+m.group(0)+"</g00>")
        
    def formatf(self,m):
        return("<f>"+m.group(0)+"</f>")
        
    def format_html(self,item):
        lb_removed = re.sub('\n|\r', "", item)
        n_removed = re.sub('N([\d|\.]+)', "", lb_removed)
        g00_formatted = re.sub('G00', self.formatg00, n_removed)
        g01_formatted = re.sub('G01', self.formatg01, g00_formatted)
        x_formatted = re.sub('X([\d|\.|-]+)', self.formatx, g01_formatted)
        y_formatted = re.sub('Y([\d|\.|-]+)', self.formaty, x_formatted)
        z_formatted = re.sub('Z([\d|\.|-]+)', self.formatz, y_formatted)
        f_formatted = re.sub('F([\d|\.]+)', self.formatf, z_formatted)
        total_string = f_formatted+"<br>\n"
        return total_string
        
if __name__ == '__main__':    
    fLoad = open("test.nc", 'r')
    GrF = GForm()
    linearray = []
    linearray.append("""
    <html>
    <head>
    <title>GCode Output</title>
    </head><body>
    <style type=\"text/css\">
    body{ font-family:sans-serif; }
    g01{ background-color: yellow; color: black; padding: 0px 15px 0px 15px; }
    f{ background-color: black; color: white; padding: 0px 15px 0px 15px; }
    g00{ background-color: black; color: yellow; padding: 0px 15px 0px 15px;}
    x{ background-color: red; color: white; padding: 0px 15px 0px 15px;}
    y{ background-color: blue; color: white; padding: 0px 15px 0px 15px;}
    z{ background-color: green; color: white; padding: 0px 15px 0px 15px;}
    </style>""")
    for line in fLoad:
        linearray.append(GrF.format_html(line))
    fLoad.close()
    linearray.append("</body></html>")
    print("".join(linearray))
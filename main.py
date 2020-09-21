# Kyle McCandless
# Experiment for web app
# 1/2/20
# To create a search engine for tennis points in web app.


import urllib.parse
import csv
import webbrowser
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith('/search'):
            self.send_response(200)
            self.end_headers()
        
            arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            filters = {}

            # Get all current filters from link
            for key, value in arguments.items():
                if key.startswith('f_'):
                    filters[key[2:]] = value[0]

            if 'field' in arguments:
                field = arguments['field'][0]
                value = arguments['value'][0]
                
                if len(field) > 0:
                    if filters.get(field) == value:
                        filters[field] = ''
                    else:    
                        filters[field] = value
                        

            self.wfile.write(self.all_points.make_html_table_string(filters).encode('utf-8'))



        elif self.path.startswith('/add'):
            self.handle_add_point()

        else:
            self.send_response(404)
            self.end_headers()


    def handle_add_point(self):
        string = '''<html>
<body><h1><center>Add Points to Tennis Point Search Engine</center></h1>
<form method="GET" action="/add"><select name="Player Name">'''

        string += create_option_string(AllPoints.dict_by_player.keys())
        #And complete this for shot, opponent, tournament, etc

        return string + '</form></body></html>'
    

    def create_option_string(keyList):
        answer = ''
        for key in keyList:
            answer += '<option value="' + key + '">' + key + '</option>'
        return answer    





class AllPoints:
    def __init__(self):
        self.dict_by_player = {}
        self.dict_by_shot = {}
        self.dict_by_opponent = {}
        self.dict_by_tournament = {}
        self.dict_by_timestamp = {}
        self.dict_by_year = {}
        self.dict_by_surface = {}

        self.player = None
        self.shot = None
        self.opponent = None
        self.surface = None
        self.tournament = None
        self.timestamp = None   

        # READ POINTS FROM FILE INTO DICT
        with open('Tennis Point List.txt', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file, strict=True)
            line_count = 0
            for row in csv_reader:
                
                time = row["timestamp"].strip()
                year = time[0:4]
                
                new_point = Point(line_count, row["link"], row["player"].strip(), row["shot"].strip(), row["opponent"].strip(), row["tournament"].strip(), time, year, row["surface"].strip())

                # add to all dicts
                add_point(self.dict_by_player, row["player"], new_point)
                add_point(self.dict_by_shot, row["shot"], new_point)
                add_point(self.dict_by_opponent, row["opponent"], new_point)
                add_point(self.dict_by_tournament, row["tournament"], new_point)
                add_point(self.dict_by_timestamp, time, new_point)
                add_point(self.dict_by_year, year, new_point)
                add_point(self.dict_by_surface, row["surface"], new_point)
                
                line_count += 1
            print(f'Read in {line_count} points.\n')

    def passes_filter(self, point, filters):
        if ('player' in filters and point.player != filters['player']) or ('shot' in filters and point.shot != filters['shot']) or ('opponent' in filters and point.opponent != filters['opponent']) or ('tournament' in filters and point.tournament != filters['tournament']) or ('timestamp' in filters and point.timestamp != filters['timestamp']) or ('surface' in filters and point.surface != filters['surface']):
            return False

        return True


    def make_html_table_string(self, filters):
        
        string = '''<html>
<body><h1><center>Tennis Point Search Engine!</center></h1>

<script language="javascript">

function add_filter(field, value) {
    var form = document.getElementById("search");
    form.value.value = value;
    form.field.value = field;

    form.submit();
}


</script>

<form method="GET" action="/search" id="search">

<input type="hidden" name="field" value="''"/>
<input type="hidden" name="value" value="''"/>

<table style="width:100%" border=5 bordercolor="FireBrick">
    <tr>
        <th>Search Criteria:</th>
        <th>Points that fit:</th>
    </tr>

    <tr>
        <td valign="top">
            <table style="width:100%">
            <tr>
                <th>Attribute:</th>
                <th>Searching for:</th>
            </tr>
            <tr>
                <td><b>Player</b>''' +  dict_keys_to_dropdown(self.dict_by_player, 'player') + '''</td>
                <td>''' + check_none(filters.get('player')) + '''</td>
            </tr>
            <tr>
                <td><b>Shot</b>''' +  dict_keys_to_dropdown(self.dict_by_shot, 'shot') + '''</td>
                <td>''' + check_none(filters.get('shot')) + '''</td>
            </tr>
            <tr>
                <td><b>Opponent</b>''' +  dict_keys_to_dropdown(self.dict_by_opponent, 'opponent') + '''</td>
                <td>''' + check_none(filters.get('opponent')) + '''</td>
            </tr>
            <tr>
                <td><b>Surface</b>''' +  dict_keys_to_dropdown(self.dict_by_surface, 'surface') + '''</td>
                <td>''' + check_none(filters.get('surface')) + '''</td>
            </tr>
            <tr>
                <td><b>Tournament</b>''' +  dict_keys_to_dropdown(self.dict_by_tournament, 'tournament') + '''</td>
                <td>''' + check_none(filters.get('tournament')) + '''</td>
            </tr>
            <tr>
                <td><b>Timestamp</b>''' +  dict_keys_to_dropdown(self.dict_by_timestamp, 'timestamp') + '''</td>
                <td>''' + check_none(filters.get('timestamp')) + '''</td>
            </tr>
            </table>
        </td>
        <td valign ="top">
            <table style="width:100%">
            <tr>
                <th></th>
                <th>Player</th>
                <th>Shot</th>
                <th>Opponent</th>
                <th>Surface</th>
                <th>Tournament</th>
                <th>Timestamp</th>
            </tr>''' 
        
        for each_list in self.dict_by_player.values():
            for each_point in each_list:
                if self.passes_filter(each_point, filters):
                    string += each_point.to_html_table()


        #pack the filters into link so we can save them
        for key,value in filters.items():
            string += '<input type="hidden" name="f_' + key + '" value="' + value + '"/>'
        
        string += "</table></form>\n</td>\n</tr>\n</table>\n</body>\n</html>"
            
        return string




    
class Point:
    def __init__(self, idnum, link, player, shot, opponent, tournament, timestamp, year, surface):
        self.idnum = idnum
        self.link = link
        self.player = player
        self.shot = shot
        self.opponent = opponent
        self.tournament = tournament
        self.timestamp = timestamp
        self.year = year
        self.surface = surface

    def display(self):
        print("   Player: " + self.player)
        print("   Shot: " + self.shot)
        print("   Opponent: " + self.opponent)
        print("   Surface: " + self.surface)
        print("   Tournament: " + self.tournament)
        print("   Timestamp: " + convert_timestamp_to_user(self.timestamp))
        print("   " + self.link + "\n")

    #Not being used now, but may be later
    #def to_html(self):
        #return '<a target="_blank" href="' + self.link + '&autoplay=1">' + self.player + ' ' + self.shot + ' vs. ' + self.opponent + ' | ' + self.tournament + ' ' + self.timestamp + ' (' + self.surface + ')</a>'

    def to_html_table(self):
        tags = '</td>\n   <td>'
        return '<tr>\n    <td><a target="_blank" href="' + self.link + '&autoplay=1">Watch!</a>' + tags + self.player + tags + self.shot + tags + self.opponent + tags + self.surface + tags + self.tournament + tags + convert_timestamp_to_user(self.timestamp) + '</td>\n</tr>'
    
    def __eq__(self, other):
        if self.idnum == other.idnum:
            return True
        return False

    def __lt__(self, other):
        return self.idnum < other.idnum
        




def add_point(dict, key, new_point):
    if key in dict:
        dict[key].append(new_point)
    else:
        dict[key] = [new_point]


def intersect(points1, points2):
    if points1 is None:
        return points2
    return [point for point in points1 if point in points2]


def dict_keys_to_string(dict):
    answer = '</br>'
    
    for key_name in sorted(dict):
        answer += '</br>' + key_name

    return answer + '</br></br>'


def dict_keys_to_dropdown(dict, dictInfo):
    answer = '</br><form method="GET" action="/search"><select name="Player Name">'
    
    for key_name in sorted(dict):
        answer += """<a href="javascript:add_filter('""" + dictInfo + """','%s')">%s</a></br>""" % (key_name, key_name)

    #Code to turn it into a select, but what do I do with the javascript:add_filter
    #answer += '<option value="' + key + '">' + key + '</option>'


        

    return answer + '</br></br>'


def print_dict_keys(dict):
    while True:
        for key_name in sorted(dict):
            print ("   " + key_name)
            
        user_input = input().strip().title()

        if user_input in dict:
            break
        else:
            print("No points with that criteria, please try again.")

    print(user_input + " added to search criteria.")
    return user_input

def print_timestamp_keys(dict):
    
    while True:
        for key_name in sorted(dict):
            print ("   " + convert_timestamp_to_user(key_name))

        user_input = input().strip().title()

        if len(user_input) == 4:
            return user_input

        if " " in user_input and "," in user_input:
                                
            converted_user_input = convert_timestamp_to_dict(user_input)

            if converted_user_input in dict:
                break

        print("No points with that criteria, please try again.")

    print(user_input + " added to search criteria.")
    return converted_user_input


def sort_all_points(one_dict):
    for points in one_dict.values():
        points.sort()


def convert_timestamp_to_user(timestamp):
    year = timestamp[0:4]
    
    month_names = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
    month = month_names.get(int(timestamp[5:7]))
    
    day = timestamp[8:10]

    return month + " " + day + ", " + year


def convert_timestamp_to_dict(timestamp):
    month_names = {"January":"01", "February":"02", "March":"03", "April":"04", "May":"05", "June":"06", "July":"07", "August":"08", "September":"09", "October":"10", "November":"11", "December":"12"}
    space_index = timestamp.index(" ")
    month = month_names.get(timestamp[0:space_index])

    comma_index = timestamp.index(",")
    day = timestamp[space_index + 1:comma_index]

    year = timestamp[comma_index + 2: comma_index + 6]

    return year + " " + month + " " + day
    

def ask_to_keep_going(message):
    while True:
        keep_going = input(message + " (Y for yes, N for no): ")
        
        if keep_going == 'Y' or keep_going == 'y':
            return True
        elif keep_going == 'N' or keep_going == 'n':
            return False
        else:
            print("Invalid input, please try again.")


def check_none(value):
    if value is None:
        return ""
    else:
        return value

            



def main():
    print("Tennis Point Search Engine Web")
    print(os.getcwd())
    
    # points are sorted by idnum, so they are loaded in sorted order ==> no need to sort them
    
    SimpleHTTPRequestHandler.all_points = AllPoints()
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
    

if __name__ == '__main__':
    main()

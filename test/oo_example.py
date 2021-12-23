from clippy.ooclippy import processDirectory
from clippy.serialization import encode_clippy_json
import json

HOWDY_EXECUTABLE_DIR = "/workspace/clippy-cpp-github.git/build/examples/oo-howdy"
processDirectory(HOWDY_EXECUTABLE_DIR)


b = Greeter()
b.setGreeting("Howdy")
b.setGreeted("Buba")

print("B greeter:", b.greet())

s = Greeter()
s.setGreeting("Mornin'")
s.setGreeted("Sissy")
print("S greeter:", s.greet())

selection = (s.letters.all > 'a') & (s.letters.all < 'z') & (s.letters.vowels < 'm') & (s.letters.consonents >= 'n'), (s.letters.vowels =='y')
print(selection)
sel_result = s[selection]
print(sel_result)


# TODO remove the "<selector>.all" stuff - the selector name should just imply all
# TODO handle return types from getitem (should return a greeter with the state set based on the filtering expression)
# TODO on the backend create a clone method that returns the json for a new greeter object based the current greeter (fillup a boost::json::object)

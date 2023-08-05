# The spellbook contains functions that generate spells, as well as helper
# functions you can use to write your own spells. Hex Client uses the 
# spellbook, but it can be used directly with Hex Connection as well:
# 
# from hex_connection import HexConnection
# hex = HexConnection()
# colorSpell = spell_color([15,15,0,220])
# hex.create_spell('my_name', 'my_spirit_animal', 'spell name', colorSpell)
# 
# The structure of every spell is the same:
#   {
#       'setup': [frames...]
#       'loop': [frames...],
#   }
# 
# Setup runs once and then loop runs forever (the total time available for 
# your program is limited by how many points you have). Each frame is composed
# of color layers, where each color layer specifies a color and then which lights
# should have that color. Here's a color layer that turns the seven center lights
# green:
#
# [ [0, 15, 0, 200], [30, 31, 32, 33, 34, 35, 36] ]

# ===============
# Built-in spells
# ===============

from random import randint

def spell_color(color):
    "Set all the lights to a color"
    validate_color(color)
    return {
        'setup': [[[color, all_lights()]]],
        'loop': None
    }

def spell_spirit(backgroundColor, spiritColor):
    """Create a spirit which runs around the outside ring, leaving a trail 
    behind her"""
    for color in [backgroundColor, spiritColor]:
        validate_color(color)
    setup = [[[backgroundColor, all_lights()]]]
    loop = []
    for i in range(18):
        loop.append([
            [backgroundColor,                           [(i) % 18]], 
            [fade(spiritColor, backgroundColor, 0.7),   [(i+1) % 18]], 
            [fade(spiritColor, backgroundColor, 0.3),   [(i+2) % 18]], 
            [spiritColor,                               [(i+3) % 18]]
        ])
    return {
        'setup': setup,
        'loop': loop
    }

def spell_flame(backgroundColor, flameColor):
    "Creates a flickering flame at the center of the Hex"
    setup = [[[backgroundColor, range(36)], [flameColor, lights_in_ring(0)]]]
    loop = []
    flameLevel = 2
    fadeColor = fade(flameColor, backgroundColor, 0.5)
    for i in range(20):
        oldFlameLevel = flameLevel
        flameLevel = randint(max(flameLevel - 1, 0), min(flameLevel + 1, 2))
        if flameLevel == oldFlameLevel:
            loop.append([[[0,0,0,0],[]]])
        elif flameLevel > oldFlameLevel:
            loop.append([
                [flameColor, lights_in_ring(flameLevel)],
                [fadeColor, lights_in_ring(flameLevel + 1)]
            ])
        else:
            loop.append([
                [fadeColor, lights_in_ring(flameLevel)],
                [backgroundColor, lights_in_ring(flameLevel + 1)]
            ])
    return {
        'setup': setup,
        'loop': loop
    }
        


# =======
# Helpers
# =======
# These functions make it easier to define the spells above.

def all_lights():
    "Returns a list of all the light numbers"
    return range(37)

def lights_in_ring(ringNumber):
    """Returns a list of all the light numbers in a ring of the hex. The center 
    light is ring 0 and the outer edge is ring 3"""
    if ringNumber not in range(4):
        raise ValueError("You can only get light rings from 0 to 3.")
    ringBoundaries = [37, 36, 30, 18, 0] 
    return range(ringBoundaries[ringNumber + 1], ringBoundaries[ringNumber])

def fade(colorOne, colorTwo, t):
    """Returns a color partway between colorOne and colorTwo. 
    t=0.0 is fully colorOne, and t=1.0 is fully colorTwo"""
    for color in [colorOne, colorTwo]:
        validate_color(color)
    return [int(round(colorOne[i] + (colorTwo[i] - colorOne[i]) * t)) for i in range(4)]


# ==========
# Validators
# ==========
# The functions below check to make sure spells are valid. It's a good idea to
# validate your spells before sending them to the server.
class InvalidSpellError(Exception):
    "An error to represent a situation where we have an invalid spell"
    pass

def validate_spell(spell, strict=True):
    "Checks to make sure a spell is valid"
    try:
        assert(isinstance(spell, dict), "tried to interpret %s as a spell, but it is not a dictionary" % spell)
        assert(spell.get('setup') or spell.get('loop'), "spell %s should define setup, loop, or both" % spell)
        for programPart in ['setup', 'loop']:
            if spell.get(programPart) is not None:
                assert(isinstance(spell.get(programPart), list), "in spell %s, %s is %s, but it should be a list if it is going to be defined" % (spell, programPart, spell.get(programPart)))
                for frame in spell.get(programPart):
                    validate_frame(frame)
    except AssertionError, message:
        if strict:
            raise InvalidSpellError(message)
        else:
            return False
    return True

def validate_frame(frame, strict=True):
    try: 
        assert(isinstance(frame, list), "tried to interpret %s as a frame, but it is not a list" % frame)
        for colorLayer in frame: 
            assert(isinstance(colorLayer, list), "color layer %s should be a list" % colorLayer)
            assert(len(colorLayer) == 2, "color layer %s should have exactly two elements: a color and a list of light numbers" % colorLayer)
            validate_color(colorLayer[0])
            lights = colorLayer[1]
            assert(isinstance(lights, list), "the second element of color layer %s should be a list of light numbers" % colorLayer)
            for lightNum in lights:
                assert(isinstance(lightNum, int), "Found %s in your list of light numbers (%s); all elements of this list should be integers" % (lightNum, lights))
    except AssertionError, message:
        if strict:
            raise InvalidSpellError(message)
        else:
            return False
    return True

def validate_color(color, strict=True):
    try: 
        assert(isinstance(color, list), "color %s should be a list" % color)
        assert(len(color) == 4, "color %s should have exactly four values" % color)
        for i, colorValue in enumerate(color):
            assert(isinstance(colorValue, int), "color value %s should be an integer" % colorValue)
            assert(0 <= colorValue, "color value %s is less than the minimum, which is 0" % colorValue)
            maxima = [15,15,15,255]
            assert (colorValue <= maxima[i], "color value %s is greater than the maximum, which is %s" % (colorValue, maxima[i]))
    except AssertionError, message:
        if strict:
            raise InvalidSpellError(message)
        else:
            return False
        return True
                
                
            

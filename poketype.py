import pyodide_http
pyodide_http.patch_all()  # This makes 'requests' work in the browser!

import requests
from pyscript import document, display

TYPINGS = ["normal", "fire", "water", "electric", "grass", "ice", "fighting", "poison", "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]

def createMappings():
    ATK_MAPPING = {}
    ATK_MAPPING["normal"] = {"rock": 0.5, "ghost": 0, "steel": 0.5}
    ATK_MAPPING["fire"] = {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2}
    ATK_MAPPING["water"] = {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5}
    ATK_MAPPING["electric"] = {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5}
    ATK_MAPPING["grass"] = {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5}
    ATK_MAPPING["ice"] = {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2, "steel": 0.5}
    ATK_MAPPING["fighting"] = {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "dark": 2, "steel": 2, "fairy": 0.5}
    ATK_MAPPING["poison"] = {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0, "fairy": 2}
    ATK_MAPPING["ground"] = {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2}
    ATK_MAPPING["flying"] = {"electric": 0.5, "grass": 2, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5}
    ATK_MAPPING["psychic"] = {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5}
    ATK_MAPPING["bug"] = {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5, "fairy": 0.5}
    ATK_MAPPING["rock"] = {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5}
    ATK_MAPPING["ghost"] = {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5}
    ATK_MAPPING["dragon"] = {"dragon": 2, "steel": 0.5, "fairy": 0}
    ATK_MAPPING["dark"] = {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5, "fairy": 0.5}
    ATK_MAPPING["steel"] = {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5, "fairy": 2}
    ATK_MAPPING["fairy"] = {"fire": 0.5, "fighting": 2, "poison": 0.5, "dragon": 2, "dark": 2, "steel": 0.5}

    DEF_MAPPING = {}
    for key in ATK_MAPPING:
        for val in ATK_MAPPING[key]:
            if val not in DEF_MAPPING:
                DEF_MAPPING[val] = {}
            DEF_MAPPING[val][key] = ATK_MAPPING[key][val]

    return ATK_MAPPING, DEF_MAPPING

def modifyMapping(type1, type2, val, atk_mapping, def_mapping):
    if val != 1:
        atk_mapping[type1][type2] = val
        def_mapping[type2][type1] = val
    else:
        if type2 in atk_mapping[type1]:
            del atk_mapping[type1][type2]
        if type1 in def_mapping[type2]:
            del def_mapping[type2][type1]

def removeInvalidTypes(typeList, atk_mapping, def_mapping):
    for t in typeList:
        del atk_mapping[t]
        del def_mapping[t]
        for key in atk_mapping:
            if t in atk_mapping[key]:
                del atk_mapping[key][t]
        for key in def_mapping:
            if t in def_mapping[key]:
                del def_mapping[key][t]

def poketypes(pokemon):
    pokemon_obj = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}")
    if pokemon_obj.status_code != 200:
        outputText = "This Pokemon doesn't exist in the database, exiting"
        document.getElementById("output").innerText = outputText
        return 0
    else:
        pokemon_dict = pokemon_obj.json()
        pokemon_types = []
        for item in pokemon_dict['types']:
            pokemon_types.append(item['type']['name'])

        return pokemon_types
    

def showTypingEffectiveness(gen, ptype, pmon, atkdef, otype, omon):
    atk_mapping, def_mapping = createMappings()
    if gen == 1:
        removeInvalidTypes(["dark", "steel", "fairy"], atk_mapping, def_mapping)
        modifyMapping("ghost", "psychic", 0, atk_mapping, def_mapping)
        modifyMapping("bug", "poison", 2, atk_mapping, def_mapping)
        modifyMapping("poison", "bug", 2, atk_mapping, def_mapping)
        modifyMapping("ice", "fire", 1, atk_mapping, def_mapping)
    elif gen < 6:
        removeInvalidTypes(["fairy"], atk_mapping, def_mapping)
        modifyMapping("ghost", "steel", 0.5, atk_mapping, def_mapping)
        modifyMapping("dark", "steel", 0.5, atk_mapping, def_mapping)

    if isinstance(ptype, str):
        ptypes = ptype.split(" ")
    else:
        ptypes = ptype
    if otype != None:
        if isinstance(otype, str):
            otypes = otype.split(" ")
        else:
            otypes = otype

    # TYPING ERROR CHECKING
    for t in ptypes:
        if not t.lower() in atk_mapping:
            outputText = f"{t} is not a valid type in gen {gen}, exiting"
            document.getElementById('output').innerText = outputText
            return
    if otype!= None:
        for t in otypes:
            if not t.lower() in atk_mapping:
                outputText = f"{t} is not a valid type in gen {gen}, exiting"
                document.getElementById('output').innerText = outputText
                return

    # MAIN
    if otype != None:
        atktypes, atkmon = otypes, omon
        deftypes, defmon = ptypes, pmon
        if atkdef == "atk":
            atktypes, atkmon = ptypes, pmon
            deftypes, defmon = otypes, omon

        outputText = ""
        if atkmon:
            outputText = f"Going through typings for {atkmon}\n"
        for atype in atktypes:
            values = atk_mapping[atype.lower()]
            val1 = 1
            if deftypes[0].lower() in values:
                val1 = values[deftypes[0].lower()]
            val2 = 1
            if len(deftypes) > 1 and deftypes[1].lower() in values:
                val2 = values[deftypes[1].lower()]
            finval = val1 * val2
            if finval == int(finval):
                finval = int(finval)
            defStr = " ".join([x.title() for x in deftypes])
            if defmon:
                defStr = defmon
            outputText += f"{atype.title()} has {finval} effectiveness on {defStr}\n"
        document.getElementById("output").innerText = outputText

    elif atkdef == "atk":
        outputText = ""
        if pmon:
            outputText = f"Going through typings for {pmon}\n"
        for i, atype in enumerate(ptypes):
            curType = atype.lower()
            values = atk_mapping[curType]
            valueMapping = {}
            for key in values:
                if not values[key] in valueMapping:
                    valueMapping[values[key]] = [key]
                else:
                    valueMapping[values[key]].append(key)
            
            non_normal_types = values.keys()
            valueMapping[1] = []
            for t in TYPINGS:
                if t.lower() in atk_mapping and not t.lower() in non_normal_types:
                    valueMapping[1].append(t)
            if valueMapping[1] == []:
                del valueMapping[1]
            
            for key in valueMapping:
                valueMapping[key] = ", ".join([x.title() for x in valueMapping[key]])

            sorted_keys = sorted(valueMapping.keys())
            outputText += f"{curType.title()} multipliers for attacking\n"
            for key in sorted_keys:
                outputText += f"{key}: {valueMapping[key]}\n"
            if i != len(ptypes) - 1:
                outputText += "\n"
        document.getElementById("output").innerText = outputText

    elif atkdef == "def":
        type1 = ptypes[0].lower()
        val1 = def_mapping[type1]
        type2 = None
        val2 = None
        if len(ptypes) > 1:
            type2 = ptypes[1].lower()
            val2 = def_mapping[type2]

        combinedDict = {}
        for t in TYPINGS:
            val = 1
            if t.lower() in def_mapping:
                if t.lower() in val1:
                    val *= val1[t.lower()]
                if val2 and t.lower() in val2:
                    val *= val2[t.lower()]
            combinedDict[t.lower()] = val

        valueMapping = {}
        for key in combinedDict:
            if not combinedDict[key] in valueMapping:
                valueMapping[combinedDict[key]] = [key]
            else:
                valueMapping[combinedDict[key]].append(key)
        
        for key in valueMapping:
            valueMapping[key] = ", ".join([x.title() for x in valueMapping[key]])

        sorted_keys = sorted(valueMapping.keys())
        defStr = ' '.join([x.title() for x in ptypes])
        if pmon:
            defStr = pmon
        outputText = f"{defStr} multipliers for defending\n"
        for key in sorted_keys:
            outputText += f"{key}: {valueMapping[key]}\n"
        document.getElementById("output").innerText = outputText

# INPUTS
def getValues(event):
    gendd = document.getElementById('generation')
    gen = int(gendd.value)
    torp1dd = document.getElementById('type-or-pokemon-1')
    torp1 = torp1dd.value
    value1inp = document.getElementById('values-1')
    if torp1 == "t":
        pmon = None
        ptype = value1inp.value
    elif torp1 == "p":
        pmon = value1inp.value
        ptype = poketypes(pmon)
        if ptype == 0:
            return
    atkdefdd = document.getElementById('atkdef')
    atkdef = atkdefdd.value
    torp2dd = document.getElementById('type-or-pokemon-2')
    torp2 = torp2dd.value
    value2inp = document.getElementById('values-2')
    if torp2 != "s":
        if torp2 == "t":
            omon = None
            otype = value2inp.value
        elif torp2 == "p":
            omon = value2inp.value
            otype = poketypes(omon)
            if otype == 0:
                return
    else:
        omon = None
        otype = None
    showTypingEffectiveness(gen, ptype, pmon, atkdef, otype, omon)

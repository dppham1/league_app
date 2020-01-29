from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
import simplejson as json
import re

## CLASSES ##

class Summoner:
    def __init__(self, summoner_name):
        self.summoner_info_json = self.get_summoner_info(summoner_name) # JSON

        if self.summoner_info_json:
            self.encrypted_summoner_id = self.summoner_info_json["id"]
            self.encrypted_acc_id = self.summoner_info_json["accountId"]

            self.name = self.summoner_info_json["name"]
            self.level = self.summoner_info_json["summonerLevel"]
            self.profile_icon_id = self.summoner_info_json["profileIconId"]
            self.profile_icon_url =  "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(GAME_VERSION, self.profile_icon_id)

            self.ranked_solo_duo_queue_type = "RANKED_SOLO_5x5"
            
            self.ranked_solo_duo_list = self.get_summoner_rank_solo_duo(self.encrypted_summoner_id)
            if self.ranked_solo_duo_list: # if the Summoner is ranked in SOLO/DUO
                self.ranked_solo_duo_json = self.ranked_solo_duo_list[0] # JSON
                
                self.ranked_solo_duo_tier = self.ranked_solo_duo_json["tier"] # the tier (i.e. DIAMOND)
                self.ranked_solo_duo = self.ranked_solo_duo_json["rank"] # the division (i.e. III)
                self.ranked_solo_duo_wins = self.ranked_solo_duo_json["wins"]
                self.ranked_solo_duo_losses = self.ranked_solo_duo_json["losses"]
            else: # if the Summoner is unranked in SOLO/DUO
                self.ranked_solo_duo_tier = "UNRANKED"
                self.ranked_solo_duo = "UNRANKED"
                self.ranked_solo_duo_wins = "None"
                self.ranked_solo_duo_losses = "None"
            
            self.matches_json = self.get_summoner_matches(self.encrypted_acc_id)
    
    def get_summoner_info(self, summoner_name): # takes in a Summoner's name, and returns a JSON object with that summoner's information
        summoner_response = requests.get(
            "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(summoner_name),
            headers = {"X-Riot-Token": API_KEY}
            )
        if summoner_response.status_code == 200:
            return json.loads(summoner_response.text)
        return None

    def get_summoner_rank_solo_duo(self, encrypted_summoner_id): # takes in a Summoner's encrypted account ID, and returns a JSON object with that summoner's ranked Solo/Duo object
        summoner_rank_response = requests.get(
            "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(encrypted_summoner_id),
            headers = {"X-Riot-Token": API_KEY}
            )
        if summoner_rank_response.status_code == 200:
            return json.loads(summoner_rank_response.text)
        return None

    def get_summoner_matches(self, encrypted_acc_id):
        summoner_matches_response = requests.get(
            "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}".format(encrypted_acc_id),
            headers = {"X-Riot-Token": API_KEY}
        )
        if summoner_matches_response.status_code == 200:
            return json.loads(summoner_matches_response.text)
        return None

class Champion:
    def __init__(self, champion_name):
        self.champion_info_json = self.get_champion_info(champion_name) # JSON

        if self.champion_info_json:
            self.id = self.champion_info_json["id"]
            self.name = self.champion_info_json["name"]
            self.title = self.champion_info_json["title"]
            self.img_url = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg".format(self.id)
            self.lore = self.champion_info_json["lore"]

            self.ally_tips = self.champion_info_json["allytips"]
            self.enemy_tips = self.champion_info_json["enemytips"]

            self.tags = self.champion_info_json["tags"]
            self.partype = self.champion_info_json["partype"]
            self.base_stats = self.champion_info_json["stats"]

            self.passive_name = self.champion_info_json["passive"]["name"]
            self.passive_description = self.clean_text(self.champion_info_json["passive"]["description"])
            self.passive_img_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/passive/{}".format(GAME_VERSION, self.champion_info_json["passive"]["image"]["full"])

            # Q
            self.q_json = self.champion_info_json["spells"][0] # JSON
            self.q_id = self.q_json["id"]
            self.q_name = self.q_json["name"]
            self.q_img_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}".format(GAME_VERSION, self.champion_info_json["spells"][0]["image"]["full"])
            self.q_description = self.clean_text(self.q_json["description"])
            self.q_tooltip = self.clean_tooltip(self.q_json, self.q_json["tooltip"])
            self.q_range = self.q_json["rangeBurn"]
            self.q_cooldown = self.q_json["cooldownBurn"]
            self.q_cost = None

            # W
            self.w_json = self.champion_info_json["spells"][1] # JSON
            self.w_id = self.w_json["id"]
            self.w_name = self.w_json["name"]
            self.w_img_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}".format(GAME_VERSION, self.champion_info_json["spells"][1]["image"]["full"])
            self.w_description = self.clean_text(self.w_json["description"])
            self.w_tooltip = self.clean_tooltip(self.w_json, self.w_json["tooltip"])
            self.w_range = self.w_json["rangeBurn"]
            self.w_cooldown = self.w_json["cooldownBurn"]
            self.w_cost = None

            # E
            self.e_json = self.champion_info_json["spells"][2] # JSON
            self.e_id = self.e_json["id"]
            self.e_name = self.e_json["name"]
            self.e_img_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}".format(GAME_VERSION, self.champion_info_json["spells"][2]["image"]["full"])
            self.e_description = self.clean_text(self.e_json["description"])
            self.e_tooltip = self.clean_tooltip(self.e_json, self.e_json["tooltip"])
            self.e_range = self.e_json["rangeBurn"]
            self.e_cooldown = self.e_json["cooldownBurn"]
            self.e_cost = None

            # R
            self.r_json = self.champion_info_json["spells"][3] # JSON
            self.r_id = self.r_json["id"]
            self.r_name = self.r_json["name"]
            self.r_img_url = "http://ddragon.leagueoflegends.com/cdn/{}/img/spell/{}".format(GAME_VERSION, self.champion_info_json["spells"][3]["image"]["full"])
            self.r_description = self.clean_text(self.r_json["description"])
            self.r_tooltip = self.clean_tooltip(self.r_json, self.r_json["tooltip"])
            self.r_range = self.r_json["rangeBurn"]
            self.r_cooldown = self.r_json["cooldownBurn"]
            self.r_cost = None

            # updates self.q_cost, self.w_cost, self.e_cost and self.r_cost
            self.update_spell_costs()

    def get_champion_info(self, champion_name): # returns the response's "data" key's champion name, not the entire object
        champion_info_response = requests.get(
        "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion/{}.json".format(GAME_VERSION, champion_name)
        )
        if champion_info_response.status_code == 200:
            response_json = json.loads(champion_info_response.text)
            return response_json["data"][champion_name]
        return None

    def clean_text(self, text): # removes all <scaleAP>, </scaleAP>, <br>, etc. tags from a string
        cleaned_text = re.sub("<.+?>", "", text) 
        return cleaned_text

    def clean_tooltip(self, spell_json, tooltip): # returns tuple of format [ ("Amumu pulls himself to them, dealing {{ e1 }} (+{{ a1 }}) magic damage and stunning for {{ e2 }} seconds", ['{{ e1 }} ', '{{ e2 }} ']) ]
        cleaned_tooltip = re.sub("<.+?>", "", tooltip) # removes all <span>, </span>, <br>, etc. tags
        placeholders = re.findall("{{ \D\d }}", tooltip) # ['{{ e1 }} ', '{{ e2 }} ']
    
        while placeholders:
            placeholder = placeholders.pop()
            letter = placeholder[3]
            index = placeholder[4]
            if letter == "e":
                try: # try and catch is used for values where placeholder, i.e. {{ e0 }}, may have a 0th index, which results in "null" value in the effectBurn array
                    cleaned_tooltip = cleaned_tooltip.replace(placeholder, spell_json["effectBurn"][int(index)])
                except: # the official Riot champion page for champions, i.e. DrMundo, has this error so we place [object Object] to purposely match Riot's error
                    cleaned_tooltip = cleaned_tooltip.replace(placeholder, "[object Object]")
            elif letter == "a":
                for key in spell_json["vars"][0]:
                    if spell_json["vars"][0][key] == letter + index:
                        cleaned_tooltip = cleaned_tooltip.replace(placeholder, str(spell_json["vars"][0]["coeff"]))
                        
        return cleaned_tooltip

    def update_spell_costs(self):
            if self.partype == "Mana" or self.partype == "Energy" or self.partype == "Fury": # determine the Q, W, E, R spells costs depending on a Champion's partype

                self.q_cost = self.q_json["costBurn"] + " {}".format(self.partype)
                self.w_cost = self.w_json["costBurn"] + " {}".format(self.partype)
                self.e_cost = self.e_json["costBurn"] + " {}".format(self.partype)
                self.r_cost = self.r_json["costBurn"] + " {}".format(self.partype)
            elif self.partype == "None": # for champions who use HP or have "No Cost" for their spells, like Garen, Katarina, DrMundo. Champions like DrMundo have a partype of None, but use HP, so the "resource" field is not "No Cost"
                if self.q_json["resource"] == "No Cost" and self.w_json["resource"] == "No Cost" and self.e_json["resource"] == "No Cost" and self.r_json["resource"] == "No Cost":
                    self.q_cost = "No Cost"
                    self.w_cost = "No Cost"
                    self.e_cost = "No Cost"
                    self.r_cost = "No Cost"
                else: # for champions who have a partype of "None", but their spells use other resources (like HP)       
                    if self.q_json["resource"] == "No Cost": # Q
                        self.q_cost = "No Cost"
                    else:
                        placeholder_q = re.findall("{{ \D\d }}", self.q_json["resource"]) # placeholder_q looks like ["{{ e1 }}"]
                        index = placeholder_q[0][4]
                        self.q_cost = self.q_json["resource"].replace(placeholder_q[0], self.q_json["effectBurn"][int(index)])

                    if self.w_json["resource"] == "No Cost": # W
                        self.w_cost = "No Cost"
                    else:
                        placeholder_w = re.findall("{{ \D\d }}", self.w_json["resource"]) # placeholder_w looks like ["{{ e1 }}"]
                        index = placeholder_w[0][4]
                        self.w_cost = self.w_json["resource"].replace(placeholder_w[0], self.w_json["effectBurn"][int(index)])
                
                    if self.e_json["resource"] == "No Cost": # E
                        self.e_cost = "No Cost"
                    else:
                        placeholder_e = re.findall("{{ \D\d }}", self.e_json["resource"])
                        index = placeholder_e[0][4]
                        self.e_cost = self.e_json["resource"].replace(placeholder_e[0], self.e_json["effectBurn"][int(index)])

                    if self.r_json["resource"] == "No Cost": # R
                        self.r_cost = "No Cost"
                    else:
                        placeholder_r = re.findall("{{ \D\d }}", self.r_json["resource"])
                        index = placeholder_r[0][4]
                        self.r_cost = self.r_json["resource"].replace(placeholder_r[0], self.r_json["effectBurn"][int(index)])
            else: # for champions like Aatrox, Yasuo, Mordekaiser who have partype as "Blood Well", "Flow", "Shield"
                self.q_cost = "No Cost"
                self.w_cost = "No Cost"
                self.e_cost = "No Cost"
                self.r_cost = "No Cost"

## ROUTES ##
                
server = Flask(__name__)

@server.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@server.route("/summoner", methods=["POST"])
def getSummonerInformation():
    summoner_searched = request.form["summoner"]
    summoner = Summoner(summoner_searched)

    if summoner.summoner_info_json == None:
        return render_template("invalid.html", error_message="Invalid Summoner searched for")
    
    return render_template(
        "summoner.html",
    
        summoner_name = summoner.name,
        summoner_level = summoner.level,

        ranked_solo_duo_tier = summoner.ranked_solo_duo_tier,
        ranked_solo_duo = summoner.ranked_solo_duo,
        
        ranked_solo_duo_wins = summoner.ranked_solo_duo_wins,
        ranked_solo_duo_losses = summoner.ranked_solo_duo_losses,
        ranked_solo_duo_queue_type = summoner.ranked_solo_duo_queue_type,
        
        profile_icon_url = summoner.profile_icon_url,
        matches = summoner.matches_json
        )

@server.route("/champions", methods=["GET"]) # endpoint that renders HTML page for the entire Champion pool sprites (9.24.2 only)
def champions():
    champions = requests.get(
        "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json".format(GAME_VERSION)
        )
    
    champions_json = json.loads(champions.text)["data"]

    champion_names_imgs = dict() # Ex: {Irelia: "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/Irelia_0.jpg"}
    for champion_name in champions_json:
        champion_names_imgs[champion_name] = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg".format(champion_name)

    return render_template("champions.html", champion_names_images=champion_names_imgs.items())

@server.route("/champion/<champion_name>", methods=["GET"])
def getChampionInfo(champion_name): # endpoint that gets a specific Champion's information (9.24.2 only)
    champion = Champion(champion_name)

    if champion.champion_info_json == None:
        return render_template("invalid.html", error_message="Invalid Champion searched for")

    return render_template(
        "champion.html",
        champion_name = champion.name,
        champion_title = champion.title,
        champion_image = champion.img_url,
        champion_lore = champion.lore,

        champion_ally_tips = champion.ally_tips,
        champion_enemy_tips = champion.enemy_tips,

        champion_tags = champion.tags,
        champion_partype = champion.partype,
        champion_base_stats = champion.base_stats,

        champion_passive_name = champion.passive_name,
        champion_passive_description = champion.passive_description,
        champion_passive_image_url = champion.passive_img_url,

        champion_q_id = champion.q_id,
        champion_q_name = champion.q_name,
        champion_q_image = champion.q_img_url,
        champion_q_description = champion.q_description,
        champion_q_tooltip = champion.q_tooltip,
        champion_q_range = champion.q_range,
        champion_q_cooldown = champion.q_cooldown,
        champion_q_cost = champion.q_cost,

        champion_w_id = champion.w_id,
        champion_w_name = champion.w_name,
        champion_w_image = champion.w_img_url,
        champion_w_description = champion.w_description,
        champion_w_tooltip = champion.w_tooltip,
        champion_w_range = champion.w_range,
        champion_w_cooldown = champion.w_cooldown,
        champion_w_cost = champion.w_cost,

        champion_e_id = champion.e_id,
        champion_e_name = champion.e_name,
        champion_e_image = champion.e_img_url,
        champion_e_description = champion.e_description,
        champion_e_tooltip = champion.e_tooltip,
        champion_e_range = champion.e_range,
        champion_e_cooldown = champion.e_cooldown,
        champion_e_cost = champion.e_cost,

        champion_r_id = champion.r_id,
        champion_r_name = champion.r_name,
        champion_r_image = champion.r_img_url,
        champion_r_description = champion.r_description,
        champion_r_tooltip = champion.r_tooltip,
        champion_r_range = champion.r_range,
        champion_r_cooldown = champion.r_cooldown,
        champion_r_cost = champion.r_cost,
        )

## MAIN ##

if __name__ == "__main__":
    API_KEY = "RGAPI-fa203917-5342-4a53-b601-13522fe20bc1"
    GAME_VERSION = "10.1.1"
    server.run(port=5000, debug=True)

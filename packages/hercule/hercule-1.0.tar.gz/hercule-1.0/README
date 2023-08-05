Hercule 1.0.0
=============

Hercule is a Python wrapper for Riot Games League of Legends API

Making Calls
------------

It's simple! To start, from hercule, import Request - this is the class you'll use to make API calls

	from hercule import Request

Hercule uses the requests module - if you're getting module errors, pip install it -

	pip install requests

Then, initialize your class - you'll need to have your API key, which you can get at https://developer.riotgames.com/sign-in

	r = Request(api_key)

From this object, you can call any of Hercule's methods and receive your information as a string or a Python dict 

Here are a few examples - 

### Getting a summoner ID

	player_id = r.get_id_from_name('Greedoid')

What this method returns is simply the player's summoner ID - useful for other methods that take it as an argument

As a note, any methods that return player information default to the North American server - if you wish to query EU-West or EU-Northeast players, just pass the server in after the player name 

	player_id = r.get_id_from_name('Froggen', 'euw')

### Getting many summoner names from a list of IDs

	bunch_of_ids = [1, 2, 3, ... 140]
	list_of_ids = r.get_names_from_ids(bunch_of_ids)

This method returns a list of names corresponding to the list of summoner IDs passed to it.

**NOTE**: This API call takes in a max of 40 IDs per call. You can pass in as many IDs as you want to the method, but you may be rate-limited if you use very large lists of IDs

### Getting the rune/mastery pages from a player

	my_runes = r.get_runes_from_name('Trick2g')
	
This returns a list of rune pages from the particular player

**NOTE**: Due to the way the Riot Games API is set up, most player information-based calls take the player's summoner ID as the argument. As such, the above method technically takes 2 API calls to Riot to make - one to convert the player name to a summoner ID, and then one, using the summoner ID, to get the player information. If you're making a lot of calls in a short period of time, it may be wise to use the functions that take summoner IDs as arguments, in order to cut down on API calls made.

	my_current_masteries = r.get_current_masteries_from_name('Trick2g')

This function goes one step further and returns only the current mastery page that the player has equipped. There is a similar function for rune pages.

### Getting statistics 

	stats = r.get_stats_summary_from_name('The Rain Man')
	ranked_stats = r.get_ranked_summary_from_name('Greedoid', 'na', 'SEASON3')

The stats summary function will retrieve overall statistics for a summoner during a particular season, while the ranked summary will return ranked information for that summoner for all queue types

**NOTE**: The statistics functions are defaulted to season 4 statistics. Since, as of this writing, season 4 has not begun yet, calling them as-is will not yield any particularly useful information. Passing in 'SEASON3', like in the ranked stats example, will allow you to see a player's performance for a past season (in this case, mine!)

### Getting champions

	champs = r.get_champions()

The default function for champions takes no parameters and returns all of the champions with regards to the North American server (for purposes of champions being disabled). get_champions has two possible arguments: region and a free-to-play flag. For example:

	euw_free_champs = r.get_champions(True, 'euw')

Will return all free champions on the EU-West server

Contact
-------

Let me know what you think - things to improve, things to remove, if I should uninstall LoL, etc.

You can get in touch with me at kjazz15@gmail.com!




This product is not endorsed, certified or otherwise approved in any way by Riot Games, Inc. or any of its affiliates.

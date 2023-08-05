import sys
import requests

class Request:

	def __init__(self, api_key):
		self.max_names = 40
		self.prior = 'http://prod.api.pvp.net/api/lol/'
		self.version = ['/v1.1', '/v1.2', '/v2.1', '/v2.2']
		self.api_key = str(api_key)

	def get_id_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/by-name/' + name 
		return self.make_request(request_string)['id']

	def get_summoner_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/by-name/' + name 
		return self.make_request(request_string)

	def get_summoner_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(summoner_id)
		return self.make_request(request_string)

	def get_masteries_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(self.get_id_from_name(name, region)) + '/masteries' 
		return self.make_request(request_string)

	def get_current_masteries_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(self.get_id_from_name(name, region)) + '/masteries' 
		raw = self.make_request(request_string)
		for page in raw['pages']:
			if page['current']: 
				return page

	def get_masteries_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(summoner_id) + '/masteries' 
		return self.make_request(request_string)
	
	def get_current_masteries_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(summoner_id) + '/masteries' 
		raw = self.make_request(request_string)
		for page in raw['pages']:
			if page['current']:
				return page

	def get_runes_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(self.get_id_from_name(name, region)) + '/runes'
		return self.make_request(request_string)

	def get_current_runes_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/summoner/' +  str(self.get_id_from_name(name, region))+ '/runes' 
		raw = self.make_request(request_string)
		for page in raw['pages']:
			if page['current']: 
				return page

	def get_runes_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(summoner_id) + '/runes' 
		return self.make_request(request_string)
	
	def get_current_runes_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/summoner/' + str(summoner_id) + '/runes' 
		raw = self.make_request(request_string)
		for page in raw['pages']:
			if page['current']:
				return page

	def get_names_from_ids(self, summoner_ids, region='na'):
		name_list = []
		for id_list in [summoner_ids[i:i+self.max_names] for i in range (0, len(summoner_ids), self.max_names)]:
			request_string = region + self.version[1] + '/summoner/' + ','.join(map(str, id_list)) + '/name'
			names = self.make_request(request_string)
			for dto in names['summoners']:
				name_list.append(dto['name'])
		return name_list

	def get_teams_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[3] + '/team/by-summoner/' + str(summoner_id) 
		return self.make_request(request_string)

	def get_teams_from_name(self, name, region='na'):
		request_string = region + self.version[3] + '/team/by-summoner/' + str(self.get_id_from_name(name, region))
		return self.make_request(request_string)

	def get_stats_summary_from_id(self, summoner_id, region='na', season='SEASON4'):
		request_string = region + self.version[1] + '/stats/by-summoner/' + str(summoner_id) + '/summary'
		return self.make_request(request_string, {'api_key' : self.api_key, 'season' : season})
	
	def get_stats_summary_from_name(self, name,  region='na', season='SEASON4'):
		request_string = region + self.version[1] + '/stats/by-summoner/' + str(self.get_id_from_name(name, region)) + '/summary'
		return self.make_request(request_string, {'api_key' : self.api_key, 'season' : season})

	def get_ranked_summary_from_id(self, summoner_id, region='na', season='SEASON4'):
		request_string = region + self.version[1] + '/stats/by-summoner/' + str(summoner_id) + '/ranked'
		return self.make_request(request_string, {'api_key' : self.api_key, 'season' : season})
	
	def get_ranked_summary_from_name(self, name,  region='na', season='SEASON4'):
		request_string = region + self.version[1] + '/stats/by-summoner/' +  str(self.get_id_from_name(name, region))+ '/ranked'
		return self.make_request(request_string, {'api_key' : self.api_key, 'season' : season})
	
	def get_leagues_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[3] + '/league/by-summoner/' + str(summoner_id) 
		return self.make_request(request_string)

	def get_leagues_from_name(self, name, region='na'):
		request_string = region + self.version[3] + '/league/by-summoner/' + str(self.get_id_from_name(name, region))
		return self.make_request(request_string)

	def get_recent_games_from_id(self, summoner_id, region='na'):
		request_string = region + self.version[1] + '/game/by-summoner/' + str(summoner_id) + '/recent'
		return self.make_request(request_string)
	
	def get_recent_games_from_name(self, name, region='na'):
		request_string = region + self.version[1] + '/game/by-summoner/' + str(self.get_id_from_name(name, region)) + '/recent'
		return self.make_request(request_string)

	def get_champions(self, ftp=False, region='na'):
		request_string = region + self.version[0] + '/champion'
		return self.make_request(request_string, {'api_key' : self.api_key, 'freeToPlay' : ftp})

	def make_request(self, request_info, info_params=None):
		if info_params is None:
			info_params = {'api_key' : self.api_key}
		try:
			r = requests.get((self.prior + request_info), params=info_params)
		except requests.exceptions.RequestException as exception:
			print exception
			sys.exit(1)
		r.raise_for_status()
		return r.json()


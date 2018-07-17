# -*- coding: utf-8 -*-
import urllib.request
import json
import re

decodex_url = "https://www.lemonde.fr/webservice/decodex/updates" 

data = {
  'satirical': {
    'root_domains': [],
    'domains_with_sub_path': [],
    'root_domains_message': "Pour information, {{match}} est satirique et à lire au second degré.",
    'domains_with_sub_path_message': "Pour information, le contenu du lien posté est satirique et à lire au second degré."
  },
  'complotist': {
    'root_domains': [],
    'domains_with_sub_path': [],
    'root_domains_message': "Attention, {{match}} diffuse des fausses actualités. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
    'domains_with_sub_path_message': "Attention, le lien posté diffuse des fausses actualités. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
  },
  'dubious': {
    'root_domains': [],
    'domains_with_sub_path': [],
    'root_domains_message': "Le lien {{match}} est questionnable. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
    'domains_with_sub_path_message': "Le lien posté est questionnable. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
  }
}

# Don't know whether the Python will be an ordered dict or not
categories = ["satirical", "complotist", "dubious"]

# Load the Decodex Data
decodex = json.loads(urllib.request.urlopen(decodex_url).read().decode('utf-8'))
sites = decodex["sites"]
urls = decodex["urls"]

# Put the URLs in the sites objects
# (the model makes more sense like this)
for url, siteID in urls.items():
  site = sites[str(siteID)]

  # If it's the first URL to be added to the site,
  # create the list 
  if len(site) < 5:
    site.append([])

  site[4].append(url)

# Put each site URL into its category
for siteID, site in sites.items():
  # Site without any URL
  if len(site) < 5:
    continue

  note = min(4, max(1, int(site[0])))

  # Ignore websites which are not a source (such as Reddit)
  if note == 4:
    continue

  notule = site[1]
  site_name = site[2]
  slug = site[3]
  urls = site[4]
  category = categories[note-1]
  data_category = data[category]

  # The ruleID for automoderator
  ruleID = '9'+siteID

  # Dispatch urls (very beautiful code here)
  for url in urls:
    if "/" in url:
      data_category['domains_with_sub_path'].append(url)
    else:
      data_category['root_domains'].append(url)

ruleIDInc = 90

for category in categories:
  data_category = data[category]

  for rule_type in ['root_domains', 'domains_with_sub_path', 'body']:
    if rule_type == 'body':
      urls = data_category['root_domains'] + data_category['domains_with_sub_path']
      sites = ", ".join(map(lambda url: "'(^|[^a-z0-9\-])%s'" % re.escape(url), urls))
      message = data_category['root_domains_message']
      rule = 'domain+title+body+url (regex)'
    else:
      urls = data_category[rule_type]
      sites = ", ".join(map(lambda url: "'%s'" % url.replace("'","\\'"), urls))
      message = data_category[rule_type + '_message']
      rule = 'domain'

    rule = """---
  # [%(ruleIDInc)s] Decodex %(category)s %(rule_type)s
  %(rule)s: [%(sites)s]
  moderators_exempt: false
  comment: |
    %(message)s

    [Source Décodex](https://www.lemonde.fr/verification/).
""" % {
      'ruleIDInc': ruleIDInc,
      'category':  category,
      'slug':      slug,
      'sites':     sites,
      'message':   message,
      'rule_type': rule_type,
      'rule':      rule
    }

    print(rule)

    ruleIDInc += 1

import statistics
import json
import os

clamp = lambda minimum, maximum, value : max(minimum, min(value, maximum))

def compute_resonance(data, weights=[2/5, 2/5, 1/5]):
	assert(abs(sum(weights) - 1) < .01)

	data['mean']  = {'F': []}
	data['stdev'] = {'F': []}

	# Remove outliers (TODO: Make configurable)
	for i in range(4):
		formant_values = [
			phoneme['F'][i] for phoneme in data['phones'] 
			if phoneme.get('F') and len(phoneme['F']) > i and phoneme['F'][i] is not None
		]
		
		if len(formant_values) == 0:
			data['mean']['F'].append(0.0)
			data['stdev']['F'].append(0.0)
			continue
		
		mean = statistics.mean(formant_values)
		stdev = statistics.stdev(formant_values) if len(formant_values) > 1 else 0.0
		data['mean']['F'].append(mean)
		data['stdev']['F'].append(stdev)
		for p in range(len(data['phones'])):
			if not data['phones'][p].get('F') or len(data['phones'][p]['F']) <= i or not data['phones'][p]['F'][i]:
				continue
			if stdev > 0 and abs(data['phones'][p]['F'][i] - mean) / stdev > 2:
				data['phones'][p]['outlier'] = True
				data['phones'][p]['F'][i] = None
				# TODO: Implement interpolation from neighboring phonemes
				# statistics.mean([
				#     data['phones'][q]['F'][i] for q in range(max(0, p-1), min(len(data['phones']), p+2)) 
				#     if data['phones'][q]['F'][i] != None
				# ])
		
	stats_path = 'stats.json'
	if os.path.exists(stats_path):
		with open(stats_path) as f:
			stats = json.loads(f.read())
	else:
		print(f"[Warning] Stats file not found at {stats_path}. Using empty stats.")
		stats = {}

	for phone in data['phones']:
		if (not (phone.get('phoneme') and 
			phone.get('expected') and 
			stats.get(phone.get('phoneme')) and 
			stats.get(phone.get('expected')))
		): continue

		if not phone['phoneme'] and phone['expected'] in stats: continue
		phone['F_stdevs'] = [
			None if len(phone['F']) <= i or phone['F'][i] == None else 
			(phone['F'][i] - stats[phone['expected']][i]['mean']) 
			/ stats[phone['expected']][i]['stdev']
			for i in list(range(4))
		]



	for i in range(len(data['phones'])):
		currentPhone = data['phones'][i]
		
		isVowel = currentPhone['phoneme'] and len([
			value for value in list(currentPhone['phoneme'])
			if value in ["A", "E", "I", "O", "U", "Y"]
		]) > 1

		if ('F_stdevs' in currentPhone  and currentPhone['F_stdevs'][1] and
			currentPhone['F_stdevs'][2] and currentPhone['F_stdevs'][3]
		):
			data['phones'][i]['resonance'] = clamp(0, 1, 
				( weights[0] * currentPhone['F_stdevs'][1] 
				+ weights[1] * currentPhone['F_stdevs'][2] 
				+ weights[2] * currentPhone['F_stdevs'][3]) / 3 + .5
			)

	pitch_sample = [
		phone['F'][0] for phone in data['phones'] 
		if phone.get('F') and phone['F'][0] and not phone.get('outlier')
	]
	resonance_sample = [
		phone['resonance'] for phone in data['phones'] 
		if phone.get('resonance') and not phone.get('outlier')
	]
	
	# Calculate statistics with safety checks
	if len(pitch_sample) > 0:
		data['meanPitch'] = statistics.mean(pitch_sample)
		data['medianPitch'] = statistics.median(pitch_sample)
		data['stdevPitch'] = statistics.stdev(pitch_sample) if len(pitch_sample) > 1 else 0.0
	else:
		data['meanPitch'] = 0.0
		data['medianPitch'] = 0.0
		data['stdevPitch'] = 0.0
	
	if len(resonance_sample) > 0:
		data['meanResonance'] = statistics.mean(resonance_sample)
		data['medianResonance'] = statistics.median(resonance_sample)
		data['stdevResonance'] = statistics.stdev(resonance_sample) if len(resonance_sample) > 1 else 0.0
	else:
		data['meanResonance'] = 0.0
		data['medianResonance'] = 0.0
		data['stdevResonance'] = 0.0

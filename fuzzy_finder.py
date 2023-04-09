def fuzzy_find(elements: list[str], query: str) -> list[str]:
	"""Fuzzy finder (Où algorithme de recherche de mots) - Renvoie une liste de mots
	correspondant le plus à un mot donné 'query' dans une list de référence 'elements'."""
	if len(query) == 0:
		return elements
	to_sort = []
	for i, el in enumerate(elements):
		count = _does_match(el, query)
		if count != -1:
			to_sort.append((count, el))
	to_sort.sort()
	return [el[1] for el in to_sort]


def _does_match(element: str, query: str) -> int:
	element = element.lower()
	query = query.lower()
	count = 0
	for c in query:
		found = element.find(c)
		count += found
		if found == -1:
			return -1
		element = element[found + 1:]
	return count

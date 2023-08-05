def checkFor(loop):
	fFound = 0
	forFound = 0
	firstBracketFound = 0
	firstSemiColonFound = 0
	secondSemiColonFound = 0
	secondBracketFound = 0
	i = 0
	print('')
	print('')
	print('\t\t==== PARSER REMARKS ====')
	print('')
	print('')
	if(len(loop)):
		while i < len(loop):
			if(loop[i] == 'f'):
				fFound = 1
				break
			i += 1
		if fFound:
			if loop[i + 1] == 'o' and loop[i + 2] == 'r':
				forFound = 1
			if forFound:
				i += 2
				while i < len(loop):
					if loop[i] == '(':
						firstBracketFound = 1
						break
					i += 1
				if firstBracketFound:
					i += 1
					while i < len(loop):
						if loop[i] == ';':
							firstSemiColonFound = 1
							break
						i += 1
					if firstSemiColonFound:
						i += 1
						while i < len(loop):
							if loop[i] == ';':
								secondSemiColonFound = 1
								break
							i += 1
						if secondSemiColonFound:
							i += 1
							while i < len(loop):
								if loop[i] == ')':
									secondBracketFound = 1
									break
								i += 1
							if secondBracketFound:
								print('No Syntax Error Found : \'for\' loop is valid')
							else:
								print('SyntaxErr : Missing right \')\' parenthesis')
						else:
							print('SyntaxErr : Missing semi-colon')
					else:
						print('SyntaxErr : Missing semi-colon')
				else:
					print('SyntaxErr : Missing left \'(\' parenthesis')
			else:
				print('SyntaxErr : Misspelled \'for\' loop')
		else:
			print('SyntaxErr: Could not find \'f\' in loop')	
	else:
		print('Could not find \'for\' loop')
	print('')
	print('')
	input('Press <ENTER> to <EXIT>')

if __name__ == '__main__':
        loop = input('Enter Loop : ')
        checkFor(loop)

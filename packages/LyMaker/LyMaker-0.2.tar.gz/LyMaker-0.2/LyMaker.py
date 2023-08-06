'''
LyMaker
@author: Acoustic E
'''
import sys, getopt,os,random
import xmlreader

VERSION = "0.2"
instances = [ 'I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XiV','XV','XVI','XVII','XVIII','XIX','XX','XXI','XXII','XXIII','XXIV','XXV','XXVI','XXVII','XXVIII','XXIX','XXX','XXXI','XXXII','XXXIII','XXXIV','XXXV','XXXVI','XXXVII','XXXVIII','XXXIX','XXXX']

def usage():
    print "LyMaker (Version %s)" % VERSION
    print "usage: LyMaker.py [options]"
    print "-h print help"
    print "-f xml filename (without extension)"
    print "-t create template xml file"

#
#
# LYMAKER
# main class
#
#

class LyMaker(object):

    durations = [64,48,32,24,16,16,16,16,16,16,12,8,8,8,6,4,4,2]
    print_durations = ['1','2.','2','4.','4','4','4','4','4','4','8.','8','8','8','16.','16','16','32']
    notepool = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
    notepool_alt = ['c','des','d','es','e','f','ges','g','as','a','bes','b']

    def __init__(self,name,quarters=4,beats=[],onbeat =False):
        self.chord = []
        self.chord.append("c")
        self.chord.append("e")
        self.chord.append("g")
        self.chord2 = []
        self.chord2.append("c")
        self.chord2.append("e")
        self.chord2.append("g")

        self.quarters = quarters
        if not len(beats):
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats
        self.onbeat = onbeat # true = bass and drums only on pulse beats
        self.meter = "moderato"
        self.tempo = 100
        self.key = "c \\major"
        self.BbKey = "d \\major"
        self.name = name
        self.modal = False # true = do not use chord root of tonic chord in bass
        self.lasttempo = 0

    def getBeats(self):
        return self.downbeats

    def getQuarters(self):
        return self.quarters

    def getChord(self):
        return self.chord

    def getChord2(self):
        return self.chord2

    def isModal(self):
        return self.modal
    
    def setKey(self,key):
        key =key.strip()
        idx = key.rfind(" ")
        k = ""
        if idx > -1:
            k = key[:idx+1]
            k += "\\"
            k += key[idx+1:]
            if key[idx+1:] == "major" or key[idx+1:] == "minor":
                self.modal = False
            else:
                self.modal = True    
        self.key = k    
        try:
            idx2 = self.notepool.index(key[:idx])
        except:
            idx2 = self.notepool_alt.index(key[:idx])
        if idx2+2 < len(self.notepool)-1:
            k = self.notepool[idx2+2]
        else:
            idx2 = idx2+2  - len(self.notepool)
            k = self.notepool[idx2]
        k += " \\"
        k += key[idx+1:]
        self.BbKey = k
        
    def setQuarters(self,quarters):
        self.quarters = quarters

    def setOnbeat(self,onbeat):
        self.onbeat = onbeat

    @classmethod
    def findDuration(self,duration):
        try:
            idx = self.durations.index(duration)
            return self.print_durations[idx]
        except:
            print "Duration %d not in list" % duration
            return ""

    def setTempo(self,tempo):
        self.tempo = tempo
        self._tempo2meter()

    def _tempo2meter(self):
        self.meter = "moderato"
        if self.tempo < 20:
            self.meter = "Larghissimo"
        elif self.tempo < 40:
            self.meter = "Grave"
        elif self.tempo < 45:
            self.meter = "Lento"
        elif self.tempo < 50:
            self.meter = "Largo"
        elif self.tempo < 55:
            self.meter = "Larghetto"
        elif self.tempo < 65:
            self.meter = "Adagio"
        elif self.tempo < 70:
            self.meter = "Adagietto"
        elif self.tempo < 73:
            self.meter = "Andante moderato"
        elif self.tempo < 78:
            self.meter = "Andante"
        elif self.tempo < 84:
            self.meter = "Andantino"
        elif self.tempo < 86:
            self.meter = "Marcia moderato"
        elif self.tempo < 98:
            self.meter = "Moderato"
        elif self.tempo < 110:
            self.meter = "Allegretto"
        elif self.tempo < 133:
            self.meter = "Allegro"
        elif self.tempo < 141:
            self.meter = "Vivace"
        elif self.tempo < 151:
            self.meter = "Vivacissimo"
        elif self.tempo < 168:
            self.meter = "Allegrissimo"
        elif self.tempo < 178:
            self.meter = "Presto"
        else:
            self.meter = "Prestissimo"

    def asXml(self):
        text = "<LyMk>\n"
        text += "<version>%s</version>\n" % VERSION
        text += "<song>\n<name>%s</name>\n" % self.name
        text += "<quarters>%d</quarters>\n" % self.quarters
        tmp = self.key.replace('\\','')
        text += "<key>%s</key>\n" % tmp
        text += "<tempo>%d</tempo>\n" % self.tempo
        text += "<structure>ABAB</structure>\n"
        text += "<downbeats>1,3</downbeats>\n"
        on = 0
        if self.onbeat == True:
            on = 1
        text += "<onbeat>%d</onbeat>\n" % on
        text += "<part>\n"
        text += "<partname>Verse</partname>\n"
        text += "<ptempo>%d</ptempo>\n" % self.tempo
        text += "<progressions>"
        text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c"
        text += "</progressions>\n"
        text += "<groove>0</groove>\n"
        text += "<drummode>0</drummode>\n"
        text += "</part>\n"
        text += "<part>\n"
        text += "<partname>Chorus</partname>\n"
        text += "<ptempo>%d</ptempo>\n" % self.tempo
        text += "<progressions>"
        text += "c,e,g|c,e,g|a,c,e|a,c,e;c,e,g|d,f,a|d,f,a|f,a,c|f,a,c"
        text += "</progressions>\n"
        text += "<groove>0</groove>\n"
        text += "<drummode>0</drummode>\n"
        text += "</part>\n"
        text += "</song>\n"
        text += "</LyMk>"
        return text


    def _downbeats(self):
        beats = [0,32]
        if self.quarters < 4:
            beats = [0] # simple duple or triple
        elif self.quarters < 6:
            beats = [0,32] # 2-2 or 2-3
        elif self.quarters == 6:
            beats = [0,48] # 3-3 compound duple
        elif self.quarters == 7:
            beats = [0,32,64] # 2-2-3 compound triple
        elif self.quarters == 8:
            beats = [0,32,64,96] # 2-2-2-2 compound quadruple
        elif self.quarters == 9:
            beats = [0,48,96] # 3-3-3 compound triple
        return beats

    def setDownbeats(self,beats):
        if len(beats)  == 0:
            self.downbeats = self._downbeats()
        else:
            self.downbeats = beats
            
    def _getRiff(self,chord):
        result = ""
        mysum = 0
        quarters = self.quarters * 16
        while mysum < quarters:
            print_dur =""
            dur = 16
            note = ""
            play = 1
            if mysum in self.downbeats:
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                dur = 16
            else:
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                play = random.randint(0,1)
                if mysum+16 > quarters:
                    slot = 0
                else:    
                    slot = random.randint(0,1)
                if slot:
                    dur = 16
                else:
                    dur = 8    
            print_dur = self.findDuration(dur)
            if play == 0:
                note = "r"
            result += note
            result += print_dur
            result += " " 
            mysum += dur    
        return result


    def _addIntro(self):
        text = '\\version "2.12.3"\n\\header {\n title = "%s"\n  composer = "LyMaker"\n  meter = "%s"\n}\n\n' % (self.name,self.meter)
        text += 'global = { \\time %d/4 }\nKey = { \\key %s }\n\n' % (self.quarters,self.key)
        return text

    def _addHarmonies(self,name,chords):
        text = '\n%s = {\n' % name
        hm = HarmonyMaker(self.quarters,self.downbeats)
        for bar in chords:
            c = bar[0]
            d = bar[0]
            if len(bar) > 1:
                d = bar[1]
            text += hm.makeChord(c,d,False)
            text += ' |\n '
        text += "\n}\n"
        return text

    def _addStructure(self,name):
        return "\\%s\n    " % (name)

    def _addScorePart(self,instanceCount,harmonies):
            text = harmonies
            text += "Trumpet = \\transpose c c' {\n\\clef treble\n\\global\n\\Key \n" 
            i = 0
            while i < instanceCount:
                text += "\\Trumpet%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Right = \\transpose c c' {\n\\clef treble\n\\global\n\\Key\n" 
            i = 0
            while i < instanceCount:
                text += "\\Right%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Left = {\n\\clef bass\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\Left%s   " % instances[i]
                i +=1
            text += "\n}\n"    
            text += 'Bass = \\transpose c c, {\n\\clef "bass_8"\n\\global\n\\Key\n'
            i = 0
            while i < instanceCount:
                text += "\\Bass%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Drums = \\drummode {\n\\global\n\\voiceOne\n"
            i = 0
            while i < instanceCount:
                text += "\\Drums%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "Cymbals = \\drummode {\n\\global\n\\voiceTwo\n"
            i = 0
            while i < instanceCount:
                text += "\\Cymbals%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "SynthR = \\transpose c c'' {\n\\clef treble\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\SynthR%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "SynthL = {\n\\clef bass\n\\global\n\\Key\n"
            i = 0
            while i < instanceCount:
                text += "\\SynthL%s   " % instances[i]
                i += 1
            text += "\n}\n"    
            text += "TenorSax = \\transpose c c' {\n\\clef treble\n\\global\n\\key %s\n\\transposition bes\n" % self.BbKey
            i = 0
            while i < instanceCount:
                text += "\\TenorSax%s   " % instances[i]
                i += 1
            text += "\n}\n"    


            text += '\npiano = {\n<<\n\\set PianoStaff.instrumentName = #"Piano"\n\\set PianoStaff.midiInstrument = #"acoustic grand"'
            text += '\n\\new Staff = "upper" \\Right\n\\new Staff = "lower" \\Left\n>>\n}\n'
            text += '\nsynth = {\n<<\n\\set PianoStaff.instrumentName = #"Synthesizer"\n\\set PianoStaff.midiInstrument = #"english horn"'
            text += '\n\\new Staff = "upper" \\SynthR\n\\new Staff = "lower" \\SynthL\n>>\n}\n'
            text += '\ntrumpet = {\n\\set Staff.instrumentName = #"Trumpet in C"\n\\set Staff.midiInstrument = #"trumpet"\n<<\n\\Trumpet\n>>\n}\n'            
            text += '\ntenorSax = {\n\\set Staff.instrumentName = #"Tenor Sax"\n\\set Staff.midiInstrument = #"tenor sax"\n<<\n\\TenorSax\n>>\n}\n'
            text += '\nbass = {\n\\set Staff.instrumentName = #"Bass"\n\\set Staff.midiInstrument = #"acoustic bass"\n<<\n\\Bass\n>>\n}\n'
            text += '\ndrumContents = {\n<<\n\\set DrumStaff.instrumentName = #"Drums"\n'
            text += '\\new DrumVoice \\Cymbals\n\\new DrumVoice \\Drums\n>>\n}\n'
            text += '\n\\score {\n <<\n  \\new StaffGroup\n  <<\n   \\new PianoStaff = "piano" \\piano\n'
            text += '   \\new PianoStaff = "synthesizer" \\synth\n'
            text += '   \\new Staff = "trumpet" \\trumpet\n'
            text += '   \\new Staff = "tenorSax" \\tenorSax\n'
            text += '   \\new Staff = "bass" \\bass\n'
            text += '   \\new ChordNames {\n      \\harmonies\n   }\n'
            text += '   \\new DrumStaff \drumContents\n  >>\n >>\n'
            text += ' \\layout { }\n \\midi {\n'
            text += '   \context {\n  \\Score\n   tempoWholesPerMinute = #(ly:make-moment %d 4)\n    }\n }\n}\n' % self.tempo
            return text

    def _makeSong(self,chords):
        result = self._addIntro()
        riff = ""
        riff2 = ""
        if len(chords) > 0:
            riff = self._getRiff(chords[0][0])
        if len (chords) > 1:    
            riff2 = self._getRiff(chords[1][0])

        result += "Riff = {\n %s |\n  %s |\n}\n\n" %(riff,riff2)
        result += "\n\n"
        riff = ""
        riff2 = ""
        if len(chords) > 0:
            riff = self._getRiff(chords[0][0])
        if len (chords) > 1:    
            riff2 = self._getRiff(chords[1][0])

        result += "RiffII = {\n %s |\n  %s |\n}\n\n" %(riff,riff2)
        result += "\n\n"

        dm = DrumMaker(self.quarters,self.downbeats,self.onbeat,5)
        result += dm.getPattern()
        result += "\n\n"
        result += dm.getDrumRoll()
        result += "\n\n"
        return result

    def _makePart(self,name,chords,instance,bassmode,drummode,tempo):
        result = ""    
        self.chord = chords[0]
        if len(chords) > 1:
            self.chord2 = chords[1]
        else:
            self.chord2 = chords[0]
        key,type = self.key.split(" ")
        hm = HarmonyMaker(self.quarters,self.downbeats)
        gm = GrooveMaker(self.quarters,key,self.downbeats,self.onbeat,bassmode,self.isModal())
        dm = DrumMaker(self.quarters,self.downbeats,self.onbeat,drummode)
        part = "% "
        part += "Part %s\n" % name
        if tempo == 0:
            tempo = self.tempo
        if tempo != self.lasttempo:
            part += "\\tempo 4 = %d\n" % tempo
            self.lasttempo = tempo
        
        resultT = "Trumpet%s =  {\n" % instance
        resultT += part
        resultT += "% range from fis, to c''\n"
        resultS = "TenorSax%s =  {\n" % instance
        resultS += part
        resultS += "% range from c to f''\n"
        resultM = "Right%s =  {\n" % instance
        resultM += part
        resultH = "Left%s = {\n" % instance
        resultH += part
        resultB = 'Bass%s = {\n' % instance 
        resultB += part
        resultD = "Drums%s = \\drummode {\n" % instance
        resultD += part
        resultC = "Cymbals%s = \\drummode {\n" % instance
        resultC += part
        resultSR = "SynthR%s =  {\n" % instance
        resultSR += part
        resultSL = "SynthL%s = {\n" % instance
        resultSL += part
        bars = 1
        length = len(chords)
        for bar in chords:
                c = bar[0]
                d = bar[0]
                if len(bar) > 1:
                    d = bar[1]
                barstr = "bar %d\n" % bars
                resultT += "% " + barstr
                resultT += " | \n"
                resultS += "% " + barstr                
                resultS += " | \n"
                resultSR += "% " + barstr
                resultSR += " | \n"
                resultSL += "% " + barstr
                resultSL += " | \n"
                resultM += "% " + barstr
                if bars % 2 and bars < length:
                    resultM += "\Riff\n"
                else:
                    resultM += ""        
                resultM += "\n"
                resultH += "% " + barstr                
                resultH += hm.makeChord(c,d,True)    
                resultH += " | \n"
                if bassmode != 5:
                    resultB += "% " + barstr                
                    resultB += gm.process(c,d)
                    resultB += " | \n"
                else:    
                    resultB += "% " + barstr
                    if bars % 2 and bars < length:
                        resultB += "\RiffII\n"
                    else:
                        resultB += ""        
                    resultB += "\n"

                resultD += "% " + barstr                
                resultD += dm.process()
                resultD += " | \n"
                resultC += "% " + barstr                
                resultC += dm.getCymbals()
                resultC += " | \n"
                bars +=1
        resultT += "}"                
        resultS += "}"                
        resultSR += "}"                
        resultSL += "}"                
        resultM += "}"
        resultH += "}"
        resultB += "}"
        resultD += "}"
        resultC += "}"
        result += resultT
        result += "\n\n"
        result += resultS
        result += "\n\n"
        result += resultSR
        result += "\n\n"
        result += resultSL
        result += "\n\n"
        result += resultM
        result += "\n\n"
        result += resultH
        result += "\n\n"
        result += resultB
        result += "\n\n"
        result += resultD
        result += "\n\n"
        result += resultC
        result += "\n\n"
        return result

    def _makeScore(self,instances,harmonies):
        result = ""
        result += self._addScorePart(instances,harmonies)
        return result

    # main routine
    # takes an xmlreader object as input
    # and generates lilypond code.
    def process(self,r):
        text = ""
        count = r.getPartCount()
        self.setTempo(r.getTempo())
        self.setKey(r.getKey())
        self.setDownbeats(r.getDownbeats())
        self.setQuarters(r.getQuarters())
        self.setOnbeat(r.isOnbeat())
        harmonies = ""
        callstring =  '\nharmonies = {\n    '
        i = 0
        while i < count:
            part = r.getPart(i)
            chords = part.progressions
            if i == 0:
                text = self._makeSong(chords)        
            i += 1
            harmonies += self._addHarmonies(part.name,chords)

        structure = r.getStructure()
        i = 0
        for s in structure:
            if i >= len(instances):
                print "more than %d actual parts, can't proceed" % i
                break
            if s < "A" or s > "Z" :
                print "invalid structure string, parts must start with uppercase A and run on alphabetically..."
                break
            offset = ord(s) - ord('A')
            part = None
            part = r.getPart(offset)
            chords = part.progressions
            bassmode = part.groove
            drummode = part.drummode
            tempo = part.tempo
            instance = instances[i]
            i += 1
            text += self._makePart(part.name,chords,instance,bassmode,drummode,tempo)
            callstring += self._addStructure(part.name)

        callstring += '}\n'
        harmonies += callstring
        text += self._makeScore(i,harmonies)
        return text

#
#
# HARMONYMAKER
#
#
class HarmonyMaker(object):
        notes = ['c','cis','d','dis','e','f','fis','g','gis','a','ais','b']
        notes_b = ['c','des','d','es','e','f','ges','g','as','a','bes','b']
        
        def __init__(self,quarters,beats):
                self.beats = beats
                self.quarters = quarters
                self.durations = self._findmymax()

        def findNote(self,note):
            try:
                idx = self.notes.index(note)
                return idx
            except:
                try:
                    idx = self.notes_b.index(note)
                except:
                    print "Chord note %s not in list" % note
                    return 0
            return idx
            
            
        def _findmymax(self):
                durations = []
                old = -1
                mymax = 0
                for b in self.beats:
                    if old > -1:
                        tmp = b - old
                        if tmp > mymax:
                            mymax = tmp
                    old = b
                durs  = [4,8,16,32,64]
                for d in durs:
                    if d > mymax:
                        break
                    durations.append(d)
                return durations
            
        # create a bar with chords only
        def makeChord(self,chord,chord2,useRest = True):
            result = ""
            cnt = 0
            pchord = ""
            while cnt < self.quarters:
                pos = cnt * 16
                if pos in self.beats or cnt == 0:
                    if pos > 0:
                        if len(chord2):
                            chord = chord2

                    pchord = "<"
                    first = True
                    last_note = 0
                    octave = 0
                    for n in chord:
                        if first == False:
                            pchord += " "
                        pchord += n
                        if first == False:
                            this_note = self.findNote(n)
                            if this_note < last_note:
                                octave += 1
                            c = 0
                            while c < octave:
                                pchord += "'"
                                c += 1    
                        first = False
                        last_note = self.findNote(n)
                    pchord += ">4 "
                    result += pchord
                else:
                    if useRest == False:
                        result += pchord
                    else:
                        result += " r4 "        
                cnt += 1    
            return result
                

#
# GROOVEMAKER
# makes the groove :-)
# bassline creator
#
class GrooveMaker(object):
        def __init__(self,quarters,key,beats,onbeat=False,bassmode=0,isModal = False):
            # beats - the downbeats
            self.beats = beats
            self.quarters = quarters
            # onbeat bass plays only on beats
            # offbeat random plays on offbeats too
            self.onbeat = onbeat
            # bassmode = 0 - random bass(offbeat) or half time bass(onbeat) [half time = plays only on downbeats]
            # bassmode = 1 - walking bass
            # bassmode = 2 - normal time bass(onbeat), no function on offbeat [ normal time = plays on all beats]
            # bassmode = 3 - double time bass(onbeat), no function on offbeat [ double time = plays on all beats, plus in the middle of the beats]
            # bassmode = 4 - shuffle bass
            # bassmode = 5 - bass riff
            # bassmode =99 - mutes  the bass
            self.bassmode = bassmode
            self.isModal = isModal # true = do not use chord root of tonic chord on 1 (offbeat) or do not at all  (onbeat)
            self.key = key # tonic of the scale
        
        # create random bass
        # consisting of eighth and sixteenth notes and rests
        # higher probability of rest on upbeats
        def process(self,chord,chord2):
            if self.bassmode == 1:
                return self._walking(chord,chord2)
            elif self.bassmode == 4:
                return self._shuffle(chord,chord2)
            elif self.bassmode == 99:
                text = ""
                i = 0
                while i < self.quarters:
                    text += " r4 "
                    i += 1    
                return text
            elif self.onbeat == True:
                return self._straight(chord,chord2)

            mysum = 0
            result = ""
            beat = 0 # downbeat 1
            dur = 8
            play = 0
            note = ""
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                if mysum in self.beats:
                    if mysum == self.beats[0]:  # beat 1
                        if self.isModal:
                            if chord[0] == self.key:
                                note = chord[1]
                            else:
                                note = chord[0]
                        else:    
                            note = chord[0]
                        play = 1 # always play on beat 1
                    else:
                        dur = 8
                        pdur = LyMaker.findDuration(dur)
                        play = 1
                        beat += 1 # next downbeat
                elif beat+1 < len(self.beats)  and mysum == (self.beats[beat+1] - 4): # one sixteenth before next downbeat
                    play = 1
                elif mysum < (self.beats[beat] + 16): # between downbeat and upbeat
                    dur = 4
                    pdur = LyMaker.findDuration(dur)
                    donotplay = random.randint(0,3)
                    if donotplay > 0:
                        play = 0
                    else:
                        play = 1
                elif mysum == (self.beats[beat] + 16): # upbeat
                    play = 0
                elif mysum > self.beats[len(self.beats)-1]: # after last downbeat
                    play = random.randint(0,1)
                else:
                    play = 0 # don't play between beat 2 and 3-8
                    if self.bassmode == 2 or self.bassmode == 3:
                        play = random.randint(0,1)
                if len(self.beats) > 1 and mysum > self.beats[1]-16:
                    if len(chord2):
                        chord = chord2

                if play > 0:
                    if note == "":
                        slot = random.randint(0,len(chord)-1)
                        note = chord[slot]
                    result += note
                    result += pdur
                    result += " "
                    note = ""
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result

        # create onbeat bass
        # consisting of eighth notes and rests
        # bass notes only on downbeats (half time)
        # or also on upbeats (normal time)
        # or also in the middle between the beats (double time)
        def _straight(self,chord,chord2):
            mysum = 0
            result = ""
            beat = 0 # downbeat 1
            dur = 8
            play = 1
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                if mysum in self.beats: # this is a downbeat
                    play = 1
                elif self.bassmode == 3 and mysum == self.beats[beat] + 8:    
                    play = 1  # double time
                elif self.bassmode == 2 and mysum == self.beats[beat] + 16:    
                    play = 1  # normal time
                elif self.bassmode == 3 and mysum == self.beats[beat] + 16:    
                    play = 1  # double time
                elif self.bassmode == 3: # play in all slot
                    play = 1  # double time
                else:
                    play = 0 # rest
                if beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                    beat += 1 # next downbeat

                if len(self.beats) > 1 and mysum > self.beats[1]-16:
                    if len(chord2):
                        chord = chord2

                if play:
                    if self.isModal:
                        if chord[0] == self.key:
                            result += chord[1]
                        else:
                            result += chord[0]
                    else:    
                        note = chord[0]
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result


        # create walking bass
        # consisting of quarter notes without rests
        def _walking(self,chord,chord2):
            mysum = 0
            result = ""
            beat = 0
            dur = 16
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                if mysum == 0:
                    if self.isModal:
                        if chord[0] == self.key:
                            result += chord[1]
                        else:
                            result += chord[0]
                    else:    
                        result += chord[0]
                    result += pdur
                    result += " "
                    mysum += dur
                    continue
                elif beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                    beat += 1
                if len(self.beats) > 1 and mysum > self.beats[1]-16:
                    if len(chord2):
                        chord = chord2
                slot = random.randint(0,len(chord)-1)
                note = chord[slot]
                result += note
                result += pdur
                result += " "
                mysum += dur
            return result

        # create shuffle bass
        # consisting of triplets of eighths without rests
        def _shuffle(self,chord,chord2):
            mysum = 0
            result = ""
            beat = 0
            dur = 16
            pdur = "8"
            while mysum < (self.quarters * 16):
                loop = 2
                result += "\\times 2/3 { "
                while loop > 0:
                    loop -= 1
                    note = ""
                    if mysum == 0 and loop == 1:
                        if self.isModal:
                            if chord[0] == self.key:
                                note = chord[1]
                            else:
                                note = chord[0]
                        else:    
                            note = chord[0]
                        note += "4"    
                    elif beat+1 < len(self.beats) and mysum == self.beats[beat+1]:
                        beat += 1
                    if len(self.beats) > 1 and mysum > self.beats[1]-16:
                        if len(chord2):
                            chord = chord2
                    if note == "":
                        slot = random.randint(0,len(chord)-1)
                        note = chord[slot]
                        if loop == 1:
                            note += "4"
                        else:    
                            note += pdur
                    result += note
                    result += " "
                    note = ""
                mysum += dur
                result += " } "
            return result

#
# DRUMMAKER
# creates a drumline
#
class DrumMaker(object):
        def __init__(self,quarters,beats,onbeat = False,mode = 0):
            self.beats = beats
            self.quarters = quarters
            self.onbeat = onbeat
            # mode 0 = bass drum, snare and (a lot of)  highhat
            # mode 1 = like 0 but with less highhat and less snare
            # mode 2 = highhat only
            # mode 3 = no bass drum
            # mode 4 = funky
            # mode 5 = pattern
            # mode 99 = no drums at all
            self.mode = mode
        
        def getPattern(self):
            text = "Drumpattern = { \\drummode { "
            i = 0
            while i < self.quarters:
                if i*16 in self.beats:
                    text += "\n  bd16 r r r" # downbeat
                else:
                    text += "\n  sn16 r r r" # upbeat
                i += 1    
            text += "\n             } }\n"
            return text
        
        def getDrumRoll(self):
            text = "Drumroll = { \\drummode { "
            # bar 1
            text += "\n<sn bd>16 <sn bd>8 sn16 sn8 sn8:32 ~ "
            text += "\nsn8 sn8 sn4:32 ~| "
            # bar 2
            text += "\nsn16 sn8 sn16 sn8 sn16 sn16 "
            text += "\nsn4 r4 | "
            text += "\n  }"
            text += "\n}\n"
            return text
            
        # random highhat
        # always play on the downbeats
        # else higher probability between downbeat and upbeat
        def getCymbals(self):
            if self.mode == 99:
                text = ""
                i = 0
                while i < self.quarters:
                    text += " r4 "
                    i += 1    
                return text
            if self.onbeat:
                return self._getCymbalsStraight()
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            pause = 1
            upbeat_factor = 5
            downbeat_factor = 1
            if self.mode == 1:
                upbeat_factor += 5
                downbeat_factor += 4
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                note = "hh"
                if mysum in self.beats: # on the downbeat
                    pause = 0
                elif mysum < self.beats[beat]+16: # before upbeat
                    pause = random.randint(0,downbeat_factor)
                else:
                    pause = random.randint(0,upbeat_factor)
                if pause == 0:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
                if beat+1 < len(self.beats):
                    if mysum == self.beats[beat+1]:
                        beat += 1
            return result
        
        # highhat Charlie Watts's style
        # highhat is always played on the downbeat and between downbeat and upbeat
        # highhat is never played on the upbeat and between upbeat and downbeat
        def _getCymbalsStraight(self):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            pause = 1
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                note = "hh"
                if mysum < self.beats[beat]+16: # before upbeat
                    pause = 0
                else:
                    pause = 1
                if pause == 0:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
                if beat+1 < len(self.beats):
                    if mysum == self.beats[beat+1]:
                        beat += 1
            return result


        # onbeat drums
        # bass drum (bd) on downbeats
        # snare drum (sn) on upbeats
        def _straight(self):
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                note = ""
                if mysum in self.beats: # downbeat
                    note = "bd"
                    if self.mode == 3:
                        play = 0
                    else:
                        play = 1
                    if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                        beat += 1
                elif (mysum % 16) == 0: # upbeat
                    play = 1
                    note = "sn"
                else:   # offbeat
                    play = 0                

                if play:
                        result += note
                        result += pdur
                        result += " "
                else:
                        result += "r"
                        result += pdur
                        result += " "
                mysum += dur
            return result

        # random offbeat drums
        # always bass drum on downbeats
        # random snare, random bass drum between down- and upbeats
        def process(self):
            if self.mode == 99 or self.mode == 2:
                text = ""
                i = 0
                while i < self.quarters:
                    text += " r4 "
                    i += 1    
                return text
            elif self.mode == 5:
                return "\\Drumpattern\n"
            if self.onbeat:
                return self._straight()
            mysum = 0
            result = ""
            beat = 0
            dur = 4
            play = 1
            pdur = LyMaker.findDuration(dur)
            while mysum < (self.quarters * 16):
                note = ""
                if mysum in self.beats: # this is a downbeat
                    note = "bd"
                    if self.mode == 3:
                        play = 0
                    else:    
                        play = 1
                    if self.mode == 4 and mysum != 0: # funky
                        note = "<bd sn>"        
                    if mysum != 0 and mysum != self.beats[len(self.beats)-1]:
                        beat += 1
                elif beat+1 < len(self.beats) and mysum == (self.beats[beat+1] - dur): # one sixteenth before next downbeat
                    play = 1
                    if self.mode == 3:
                        play = 0
                    note = "bd"
                elif mysum < (self.beats[beat] + 16): # between downbeat and upbeat
                    prop = 3
                    if self.mode == 4:
                        prop = 2
                    donotplay = random.randint(0,prop)
                    play = 0
                    if donotplay == 0 and self.mode != 3:
                        play = 1
                    if beat == 0:
                        play = 0
                    note = "bd"
                elif mysum > self.beats[len(self.beats)-1]: # after last downbeat
                    play = random.randint(0,1)
                    note = "sn"
                elif mysum == self.beats[beat]+16: # this is a upbeat
                    play = 1
                    note = "sn"
                    if self.mode == 4 and beat == 0:
                        play = 0 # funky, no snare on first upbeat
                else: # between upbeat and downbeat
                    prop = 3
                    if self.mode == 0 or self.mode == 3 or self.mode == 4:
                        prop = 1
                    donotplay = random.randint(0,prop)
                    play = 0
                    if donotplay == 0:
                        play = 1
                    note = "sn"
                    if self.mode == 4 and beat == 0:
                        play = 0 # funky, no snare on first upbeat
                    

                if play:
                    result += note
                    result += pdur
                    result += " "
                else:
                    result += "r"
                    result += pdur
                    result += " "
                mysum += dur
            return result


#
# MAIN
# isn't it?
#
#
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htf:", ["help","template","file="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    automatic = False
    template = False
    filename = "default"
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            filename = a
            automatic = True
        elif o in ("-t", "--template"):
            template = True
    mm = LyMaker(filename)
    if automatic:
        r = xmlreader.xmlreader(filename+ ".xml")
        r.importXML()
        text = mm.process(r)
        outf = None
        try:
            outf = open(filename + ".ly","w")
        except:
            print "Cannot open %s" % (filename + ".ly")
        if outf:    
            outf.write(text)
            outf.flush()
            outf.close
    elif template:
        outf = None
        try:
            outf = open("template.xml","w")
        except:
            print "Cannot open %s" % ("template.ly")
        if outf:    
            outf.write(mm.asXml())
            outf.flush()
            outf.close

        
    sys.exit()

if __name__ == '__main__':
    main()


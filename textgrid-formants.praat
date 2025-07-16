#!/usr/bin/env praat
# Simple Praat script for formant analysis
# This is a placeholder - requires actual Praat installation

form Extract formants from TextGrid
    sentence Sound_file
    sentence TextGrid_file
endform

# Read files
sound = Read from file: sound_file$
textgrid = Read from file: textGrid_file$

# Create formant object
selectObject: sound
formant = To Formant (burg): 0, 5, 5500, 0.025, 50

# Extract data
selectObject: textgrid
numberOfIntervals = Get number of intervals: 2

writeInfoLine: "Words:"
for i from 1 to numberOfIntervals
    selectObject: textgrid
    label$ = Get label of interval: 1, i
    if label$ <> ""
        start = Get starting point: 1, i
        writeInfo: fixed$(start, 3), tab$, label$, newline$
    endif
endfor

writeInfoLine: "Phonemes:"
numberOfPhonemes = Get number of intervals: 2
for i from 1 to numberOfPhonemes
    selectObject: textgrid
    label$ = Get label of interval: 2, i
    if label$ <> ""
        start = Get starting point: 2, i
        end = Get end point: 2, i
        midpoint = (start + end) / 2
        
        selectObject: formant
        f1 = Get value at time: 1, midpoint, "Hertz", "Linear"
        f2 = Get value at time: 2, midpoint, "Hertz", "Linear"
        f3 = Get value at time: 3, midpoint, "Hertz", "Linear"
        f4 = Get value at time: 4, midpoint, "Hertz", "Linear"
        
        if f1 = undefined
            f1$ = "--"
        else
            f1$ = fixed$(f1, 0)
        endif
        
        if f2 = undefined
            f2$ = "--"
        else
            f2$ = fixed$(f2, 0)
        endif
        
        if f3 = undefined
            f3$ = "--"
        else
            f3$ = fixed$(f3, 0)
        endif
        
        if f4 = undefined
            f4$ = "--"
        else
            f4$ = fixed$(f4, 0)
        endif
        
        writeInfo: fixed$(start, 3), tab$, label$, tab$, f1$, tab$, f2$, tab$, f3$, tab$, f4$, newline$
    endif
endfor

# Clean up
removeObject: sound, textgrid, formant
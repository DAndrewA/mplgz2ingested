; $Id: dloadct.pro,v 1.7 2003/08/29 14:44:23 dturner Release_ddt_1_13 $
;***********************************************************************************
;+
;Abstract:
; This function loads up the new colortable in VIP_HOME/idl/lib instead of the
;       table included in the nominal IDL distribution.
;
;     INPUTS:	X, Color table number to load
;
;     OUTPUTS:	None
;
;     CALLS: 	loadct
;
; Call:
    pro dloadct, x, opsys=opsys
;-


  file = getenv("IDLTOOLS_HOME") + '/lib/colors1.tbl'

	if (keyword_set(opsys) eq 0) then opsys = 0

	if (opsys ne 1) then begin
		; Check to see if the file exists
;		command = 'echo "if (-e ' + file + ') echo 1" | csh -fst'
;		spawn, command, result
;		result = fix(result(n_elements(result)-1))
          result = file_test (file)
	endif else begin
          file = getenv("VAP_HOME") + '\colors1.tbl' ; temporary fix by jgold
;          result=1
          result = file_test (file)
  endelse

  nparms = n_params()

  if(nparms eq 1) then begin
    if(result eq 1) then loadct, x, file=file $
;    else if(alt_result eq 1) then loadct, x, file=alt_file $
    else begin
      if(x le 40) then loadct, x $
      else begin
        print,'*** Unable to find the color table file ' + file + ' ***'
        print,'*** Default color table 0 loaded instead ***'
        loadct,0
      endelse
    endelse
  endif else begin
    if(result eq 1) then loadct, file=file $
    else begin
      print,'*** Unable to find the color table file ' + file + ' ***'
      loadct
    endelse
  endelse

  return
end

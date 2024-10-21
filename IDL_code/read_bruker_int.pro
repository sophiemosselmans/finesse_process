PRO read_bruker_int,number_scans,intname,centre_set,ints

centre_set=LONARR(number_scans)

        FOR int_s=0,number_scans-1 DO BEGIN
          filen=intname(int_s)
          openr,file,filen,/get_lun  ;open the .ssp file  
          DUM=FSTAT(file)
          dum_sz=long(dum.(15)/4)
          IF dum_sz GT 57254L THEN dum_sz=57254L
          dummy_int=fltarr(dum_sz)
          readu,file,dummy_int
          close,file
          free_lun,file
           
            ;****************************************************************************************************************
            discard=400L  ;The start and end of the interferograms are filled with rubbish, this gets rid of these values to allow determination of ZPD
            dummy_int2=fltarr(57254)
            dummy_int2(0L:dum_sz-1L)=dummy_int(0L:dum_sz-1L)
            dummy_int2(0:discard)=0.
            dummy_int2(57253-(discard+1):57253)=0.
            zeropd=max(dummy_int2^2,subscript)
            centre_set(int_s)=subscript
            ;****************************************************************************************************************
            ints(int_s,0:57253)=dummy_int2(*)
         
        ENDFOR   ;loop over number of scans per view

END
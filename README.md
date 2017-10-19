Stab
----
###### (S)earch (Tab)delimited

#### Usage:
    **Single Column**
    Search Column1 for Value1

        stab -c"Column1:Value1" File.txt


    **Multiple Columns:**
    Search Column1 for Value1 and Column2 for Value2.

        **And Statement:**
        stab -c"Column1,Column2||Value1,Value2" File.txt

        **Or Statement:**
        stab -c"Column1:Value1" -c"Column2:Value2:!=" File.txt


#### Todos:
- [x] Print all lines
- [x] Print lines based on definitions given in "-c" option
- [x] Print headers defined by the "-h" option
- [x] Print all headers minus those defined in the "-^h" option
- [x] Print ignore case in searches
- [x] Allow for custom delimiter
- [x] Print available headers
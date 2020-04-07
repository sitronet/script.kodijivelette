English version

Hello,

I've been looking for a way to display information on the music I listen to on my television for a long time.
My television being connected to a raspberry box with kodi, it seemed natural to me to use this one to display
the information and covers of discs stored on my LogitechMediaServer, moreover I only use players
completely independent of my TV and Kodi (squeezebox, picoreplayer, max2play). While searching, I found addons that run on
Kodi as Bossanova's Xsqueeze and most recently the macerlveldt's Squeezebox audio plugin. Neither gives me
satisfaction. The bossanova program only runs partially at home and again after having made some hacks
 in the code whose undo this fiery guitar background, while the audio plugin from marcel does not work outright
 since it is absolutely necessary to install squeezelite on the Kodi station, which I neither want nor need.
 I tried to get my hands  to modify according to my wishes but I quickly understood that
 I did not understand anything about their coding logic and that to try to move forward it would be more educational for me
 to write new code in python. so I turned to writing python code, starting at the beginning
 ie installing an IDE, reading the python doc, testing simple examples of data structures, threads,
 etc ... reading the libraries for Kodi Addon then start the embryo of the application in addon for kodi.
 Pretty quickly I found myself on a new pitfall, I did not understand anything about the logic of kodi for the placement
of elements on the screen. I was definitely going to give up this jumble of skin file in XML when by chance I came across
 the pyxbmct library of Roman_V_M. The path of the coding of the display has suddenly cleared up, finally something,
 that I who follow from the old school understood. I could finally consider having the display of the covers
 of my records on my TV. Good this with a few hours of hard coding on my computer and also a few more
 readings to understand the functioning of the music server communication model and also the programming
 object in python. Of course after a few setbacks and poor understanding of object programming I have something
  not perfect made of odds and ends which satisfies me in that I can display my music library and my two radios
  favorite (radio paradise and Fip Bordeaux), that's the main thing. It's not over, will it ever be?
  it is full of bugs, it adds to its charm but it is me who do it with my little brain and my fluff
  strumming on the keyboard. I am very proud of it, displeased by the purists who will find the faults in reading
  of a novice. For the rest if this little program can satisfy you I will be very comfortable, it is at your disposal
  under the terms of the GNU-GPL or CECILL license
  
  What should work:
  
  - Display of music in progress (it was my initial goal)
  - route and selection of radios, some applications and favorites
  - tour of artists, albums, repertoires and random tracks
  
  What did not work for the moment in this alpha version (but should word in the 0.0.d):
  - Player selection (random choice of program)
  - modification of the player volume
  - turn on/off the player
   
to note: You can always control from a smartphone (for example with Squeezer app) the missing functions
while displaying on the screen the music playing.
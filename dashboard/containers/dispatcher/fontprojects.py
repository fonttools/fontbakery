#!/usr/bin/env python
git_repos = [
  ["Adamina", "https://github.com/cyrealtype/Adamina.git", "fonts/Adamina-"],
  ["Abhaya Libre", "https://github.com/mooniak/abhaya-libre-font", "fonts/ttf/AbhayaLibre-"],
  ["Adobe Blank", "https://github.com/adobe-fonts/adobe-blank", "AdobeBlank"],
  ["Anaheim", "https://github.com/vernnobile/anaheimFont", "Anaheim-"],
  ["Alike", "https://github.com/cyrealtype/Alike.git", "Alike-"],
  ["Amita", "https://github.com/etunni/Amita.git", "TTF/Amita-"],
  ["Arya", "https://github.com/etunni/Arya.git", "TTF/Arya-"],
  ["Asar", "https://github.com/EbenSorkin/Asar.git", "Asar-"],
  ["Atomic Age", "https://github.com/EbenSorkin/Atomic-Age.git", "fonts/ttf/AtomicAge-"],
  ["Biryani", "https://github.com/typeoff/biryani", "Font Files/TTFs with ttautohints/Biryani-"],
  # Note: There's also Biryani without autohints.
  # TTX-ONLY: ["Baloo", "https://github.com/girish-dalvi/Baloo", "TTX/Baloo-"],
  # TTX-ONLY: ["BalooBhai", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhai-"],
  # TTX-ONLY: ["BalooBhaijaan", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhaijaan-"],
  # TTX-ONLY: ["BalooBhaina", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhaina-"],
  # TTX-ONLY: ["BalooChettan", "https://github.com/girish-dalvi/Baloo", "TTX/BalooChettan-"],
  # TTX-ONLY: ["BalooDa", "https://github.com/girish-dalvi/Baloo", "TTX/BalooDa-"],
  # TTX-ONLY: ["BalooPaaji", "https://github.com/girish-dalvi/Baloo", "TTX/BalooPaaji-"],
  # TTX-ONLY: ["BalooTamma", "https://github.com/girish-dalvi/Baloo", "TTX/BalooTamma-"],
  # TTX-ONLY: ["BalooTammudu", "https://github.com/girish-dalvi/Baloo", "TTX/BalooTammudu-"],
  # TTX-ONLY: ["BalooThambi", "https://github.com/girish-dalvi/Baloo", "TTX/BalooThambi-"],
  ["Basic", "https://github.com/EbenSorkin/Basic.git", "Basic-"],
  ["Bhavuka", "https://github.com/10four/Bhavuka.git", "Bhavuka-"],
  ["Cabin", "https://github.com/impallari/Cabin.git", "fonts/TTF/Cabin-"],
  ["Cambay", "https://github.com/anexasajoop/cambay.git", "cambay/Font files/Unhinted/CambayDevanagari-"],
  ["Catamaran Tamil", "https://github.com/VanillaandCream/Catamaran", "Fonts/Catamaran-"],
  ["Chonburi", "https://github.com/cadsondemak/chonburi.git", "fonts/Chonburi-"],
  ["Coda", "https://github.com/vernnobile/CodaFont", "coda/in-progress/Regular/Coda"], # BAD REPO!
  # Note: Coda's repo has a bad tree structure (one weight per folder). There's also a "Heavy".
  ["Cormorant", "https://github.com/CatharsisFonts/Cormorant.git", "1. TrueType Font Files/Cormorant-"],
  ["Cutive Mono", "https://github.com/vernnobile/CutiveFont", "CutiveMono/GWF-1.001/CutiveMono-"],
  # Note: There's also Cultive Roman.
  # OTF-ONLY: ["Datalegreya", "https://github.com/figs-lab/datalegreya", ""], # sources with OTF binaries, but no TTFs.
  ["Dekko", "https://github.com/EbenSorkin/Dekko.git", "Dekko-"],
  # SOURCE-ONLY (UFO): ["Dhurjati", "https://github.com/appajid/dhurjati", "Dhurjati.ufo"],
  ["Dhyana", "https://github.com/vernnobile/DhyanaFont", "Regular/Dhyana"], # BAD REPO!
  # Note: Dhyana's repo has a bad tree structure (one weight per folder). There's also a "Bold".
  # FONTBAKERY BUG: ["Digital Numbers", "https://github.com/s-a/digital-numbers-font", "gh-pages/dist/DigitalNumbers-"],
  # Note: The above requires adding to FB support for cloning a repo from a different branch (such as gh-pages)
  ["Dinah", "https://github.com/elms-/Dinah", "DINAHv1.3/DINAH"], # BAD REPO: NON-CANONICAL NAMES!
  # TTX-ONLY: ["Eczar", "https://github.com/rosettatype/Eczar", "fonts/ttf/Eczar-"],
  # TTX-ONLY: ["Mukta Devanagari", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/Mukta-Devanagari/Mukta-"],
  # TTX-ONLY: ["MuktaMalar Tamil", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/MuktaMalar-Tamil/MuktaMalar-"],
  # TTX-ONLY: ["MuktaVaani Gujarati", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/MuktaVaani-"],
  ["Federant", "https://github.com/cyrealtype/Federant.git", "Federant-"],
  ["Fira", "https://github.com/mozilla/Fira", "ttf/FiraSans-"],
  # Note: The above has got good names, but also some extra like "FiraSans-BookItalic.ttf" (may be treated as a separate family?)
  # TTX-ONLY: ["Fruktur", "https://github.com/EbenSorkin/Fruktur", "TTX/TTF/Fruktur-"],
  # SOURCE-ONLY (UFO): ["Gidugu", "https://github.com/appajid/gidugu", "Gidugu.ufo"],
  ["Glegoo", "https://github.com/etunni/glegoo.git", "Glegoo-"],
  # OTF-ONLY: ["Gurajada", "https://github.com/appajid/gurajada", ""],
  # OTF-ONLY: ["Hind Colombo", "https://github.com/itfoundry/hind-colombo", "build/HindColombo-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Guntur", "https://github.com/itfoundry/hind-guntur", "build/HindGuntur-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Jalandhar", "https://github.com/itfoundry/hind-jalandhar", "build/HindJalandhar-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Kochi", "https://github.com/itfoundry/hind-kochi", "build/HindKochi-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Madurai", "https://github.com/itfoundry/hind-madurai", "build/HindMadurai-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Mysuru", "https://github.com/itfoundry/hind-mysuru", "build/HindMysuru-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Siliguri", "https://github.com/itfoundry/hind-siliguri", "build/HindSiliguri-"], # sources with OTF binaries, but no TTFs.
  # OTF-ONLY: ["Hind Vadodara", "https://github.com/itfoundry/hind-vadodara", "build/HindVadodara-"], # sources with OTF binaries, but no TTFs.
  ["Homenaje", "https://github.com/googlefonts/Homenaje.git", "fonts/Homenaje-"],
  # GFONTS REPO: {"Inconsolata", "https://github.com/google/fonts/tree/master/ofl/inconsolata", "ofl/inconsolata/Inconsolata-"}, # too large to checkout!
  ["Inknut Antiqua", "https://github.com/clauseggers/Inknut-Antiqua.git", "TTF-OTF/InknutAntiqua-"],
  ["Itim", "https://github.com/cadsondemak/itim.git", "fonts/Itim-"],
  # FONTBAKERY BUG: ["Jaldi", "https://github.com/Omnibus-Type/Jaldi", "gh-pages/Fonts/Jaldi-"], # add support for gh-pages branch
  ["Jura", "https://github.com/ossobuffo/jura", "fonts/ttf/Jura-"],
  ["Kadwa", "https://github.com/solmatas/Kadwa", "Kadwa Font Files/Kadwa-"],
  # Note: There's also a "Kadwa Cyrillic" in this repo, but only Glyphs source files. No TTF binaries.
  # OTF-ONLY: ["Kalam", "https://github.com/itfoundry/kalam", "build/Kalam-"], # sources with OTF binaries, but no TTFs.
  ["Kanit", "https://github.com/cadsondemak/kanit.git", "font/Kanit-"],
  ["Kavoon", "https://github.com/EbenSorkin/Kavoon.git", "Kavoon-"],
  # OTF-ONLY: ["Khand", "https://github.com/itfoundry/khand", "build/Khand-"], # sources with OTF binaries, but no TTFs.
  ["Khula", "https://github.com/erinmclaughlin/Khula.git", "ttf_hinted/Khula-"],
  ["Kurale", "https://github.com/etunni/kurale.git", "fonts/Kurale-"],
  ["Lato", "https://github.com/googlefonts/LatoGFVersion.git", "fonts/Lato-"],
  # SOURCE-ONLY (UFO): ["Lakkireddy", "https://github.com/appajid/lakkireddy", "LakkiReddy.ufo"],
  #["Mallanna", "https://github.com/appajid/mallanna", ""],
  #["Mandali", "https://github.com/appajid/mandali", ""],
  #["Martel", "https://github.com/typeoff/martel", ""],
  #["Martel Sans", "https://github.com/typeoff/martel_sans", ""],
  #["Merriweather Sans", "https://github.com/EbenSorkin/Merriweather-Sans", ""],
  #["Modak", "https://github.com/girish-dalvi/Modak", ""],
  #["Monda", "https://github.com/vernnobile/mondaFont", ""],
  #["Nats", "https://github.com/appajid/nats", ""],
  #["Ntr", "https://github.com/appajid/ntr", ""],
  #["Padauk", "https://github.com/silnrsi/font-padauk", ""],
  #["Palanquin", "https://github.com/VanillaandCream/Palanquin", ""],
  #["Peddana", "https://github.com/appajid/peddana", ""],
  ["Poiret One", "https://github.com/alexeiva/poiretone.git", "fonts/ttf/PoiretOne-"],
  #["Ponnala", "https://github.com/appajid/ponnala", ""],
  #["Poppins", "https://github.com/itfoundry/poppins", ""],
  #["Pragati Narrow", "https://github.com/Omnibus-Type/PragatiNarrow", ""],
  ["Quicksand", "https://github.com/andrew-paglinawan/QuicksandFamily.git", "fonts/Quicksand-"],
  ["Raleway", "https://github.com/impallari/Raleway.git", "fonts/v3.000 Fontlab/TTF/Raleway-"],
  #["Ranga", "https://github.com/antonxheight/Ranga", ""],
  #["Ramabhadra", "https://github.com/appajid/ramabhadra", ""],
  #["Ramaraja", "https://github.com/appajid/ramaraja", ""],
  #["Raviprakash", "https://github.com/appajid/raviprakash", ""],
  ["Redacted", "https://github.com/christiannaths/Redacted-Font.git", "src/Redacted-"],
  ["Rhodium Libre", "https://github.com/DunwichType/RhodiumLibre.git", "RhodiumLibre-"],
  #["Rozhaone", "https://github.com/itfoundry/rozhaone", ""],
  #["Sahitya", "https://github.com/juandelperal/sahitya", ""],
  ["Sarala", "https://github.com/huertatipografica/sarala.git", "font/Sarala-"],
  #["Silson", "https://github.com/simoncozens/silson", ""],
  #["Sitara", "https://github.com/Neelakash/sitara", ""],
  #["Slabo", "https://github.com/TiroTypeworks/Slabo", ""],
  #["Source Serif Pro", "https://github.com/adobe/source-serif-pro", ""],
  #["Sreekrushnadevaraya", "https://github.com/appajid/sreekrushnadevaraya", ""],
  ["Sriracha", "https://github.com/cadsondemak/sriracha.git", "fonts/Sriracha-"],
  ["Sumana", "https://github.com/cyrealtype/Sumana.git", "Sumana-"],
  ["Sura", "https://github.com/huertatipografica/sura.git", "fonts/Sura-"],
  #["Suranna", "https://github.com/appajid/suranna", ""],
  #["Suravaram", "https://github.com/appajid/suravaram", ""],
  #["Tenaliramakrishna", "https://github.com/appajid/tenaliramakrishna", ""],
  #["Tillana", "https://github.com/itfoundry/tillana", ""],
  #["Timmana", "https://github.com/appajid/timmana", ""],
  #["TrocchiFont", "https://github.com/vernnobile/TrocchiFont", ""],
  ["Varela Round Hebrew", "https://github.com/alefalefalef/Varela-Round-Hebrew.git", "fonts/VarelaRound-"],
  ["Varta", "https://github.com/EbenSorkin/Varta.git", "Varta-"],
  #["Vesper Libre", "https://github.com/motaitalic/vesper-libre", ""],
  #["Work Sans", "https://github.com/weiweihuanghuang/Work-Sans", ""],
  #["Yantramanav", "https://github.com/erinmclaughlin/Yantramanav", ""]
]

if __name__ == '__main__':
  print ("There are {} font repositories listed in this file.".format(len(git_repos)))

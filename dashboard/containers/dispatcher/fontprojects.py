#!/usr/bin/env python
git_repos = [
  #["STATUS", "FAMILY-NAME", "GIT-REPO-URL", "FONTFILES-PREFIX"],
  ["OK", "Adamina", "https://github.com/cyrealtype/Adamina.git", "fonts/Adamina-"],
  ["OK", "Abhaya Libre", "https://github.com/mooniak/abhaya-libre-font", "fonts/ttf/AbhayaLibre-"],
  ["OK", "Adobe Blank", "https://github.com/adobe-fonts/adobe-blank", "AdobeBlank"],
  ["OK", "Anaheim", "https://github.com/vernnobile/anaheimFont", "Anaheim-"],
  ["OK", "Alike", "https://github.com/cyrealtype/Alike.git", "Alike-"],
  ["OK", "Amita", "https://github.com/etunni/Amita.git", "TTF/Amita-"],
  ["OK", "Arya", "https://github.com/etunni/Arya.git", "TTF/Arya-"],
  ["OK", "Asar", "https://github.com/EbenSorkin/Asar.git", "Asar-"],
  ["OK", "Atomic Age", "https://github.com/EbenSorkin/Atomic-Age.git", "fonts/ttf/AtomicAge-"],
  ["NOTE", "Biryani", "https://github.com/typeoff/biryani", "Font Files/TTFs with ttautohints/Biryani-"],
  # Note: There's also Biryani without autohints.
  ["TTX", "Baloo", "https://github.com/girish-dalvi/Baloo", "TTX/Baloo-"],
  ["TTX", "BalooBhai", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhai-"],
  ["TTX", "BalooBhaijaan", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhaijaan-"],
  ["TTX", "BalooBhaina", "https://github.com/girish-dalvi/Baloo", "TTX/BalooBhaina-"],
  ["TTX", "BalooChettan", "https://github.com/girish-dalvi/Baloo", "TTX/BalooChettan-"],
  ["TTX", "BalooDa", "https://github.com/girish-dalvi/Baloo", "TTX/BalooDa-"],
  ["TTX", "BalooPaaji", "https://github.com/girish-dalvi/Baloo", "TTX/BalooPaaji-"],
  ["TTX", "BalooTamma", "https://github.com/girish-dalvi/Baloo", "TTX/BalooTamma-"],
  ["TTX", "BalooTammudu", "https://github.com/girish-dalvi/Baloo", "TTX/BalooTammudu-"],
  ["TTX", "BalooThambi", "https://github.com/girish-dalvi/Baloo", "TTX/BalooThambi-"],
  ["OK", "Basic", "https://github.com/EbenSorkin/Basic.git", "Basic-"],
  ["OK", "Bhavuka", "https://github.com/10four/Bhavuka.git", "Bhavuka-"],
  ["OK", "Cabin", "https://github.com/impallari/Cabin.git", "fonts/TTF/Cabin-"],
  ["OK", "Cambay", "https://github.com/anexasajoop/cambay.git", "cambay/Font files/Unhinted/CambayDevanagari-"],
  ["OK", "Catamaran Tamil", "https://github.com/VanillaandCream/Catamaran", "Fonts/Catamaran-"],
  ["OK", "Chonburi", "https://github.com/cadsondemak/chonburi.git", "fonts/Chonburi-"],
  ["NOTE", "Coda", "https://github.com/vernnobile/CodaFont", "coda/in-progress/Regular/Coda"], # BAD REPO!
  # Note: Coda's repo has a bad tree structure (one weight per folder). There's also a "Heavy".
  ["OK", "Cormorant", "https://github.com/CatharsisFonts/Cormorant.git", "1. TrueType Font Files/Cormorant-"],
  ["NOTE", "Cutive Mono", "https://github.com/vernnobile/CutiveFont", "CutiveMono/GWF-1.001/CutiveMono-"],
  # Note: There's also Cultive Roman.
  ["OTF", "Datalegreya", "https://github.com/figs-lab/datalegreya", ""], # sources with OTF binaries, but no TTFs.
  ["OK", "Dekko", "https://github.com/EbenSorkin/Dekko.git", "Dekko-"],
  ["UFO", "Dhurjati", "https://github.com/appajid/dhurjati", "Dhurjati"],
  ["NOTE", "Dhyana", "https://github.com/vernnobile/DhyanaFont", "Regular/Dhyana"], # BAD REPO!
  # Note: Dhyana's repo has a bad tree structure (one weight per folder). There's also a "Bold".
  ["GH-PAGES", "Digital Numbers", "https://github.com/s-a/digital-numbers-font", "gh-pages/dist/DigitalNumbers-"],
  # Note: The above requires adding to FB support for cloning a repo from a different branch (such as gh-pages)
  ["OK", "Dinah", "https://github.com/elms-/Dinah", "DINAHv1.3/DINAH"], # BAD REPO: NON-CANONICAL NAMES!
  ["TTX", "Eczar", "https://github.com/rosettatype/Eczar", "fonts/ttf/Eczar-"],
  ["TTX", "Mukta Devanagari", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/Mukta-Devanagari/Mukta-"],
  ["TTX", "MuktaMalar Tamil", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/MuktaMalar-Tamil/MuktaMalar-"],
  ["TTX", "MuktaVaani Gujarati", "https://github.com/girish-dalvi/Ek-Mukta", "TTX/MuktaVaani-"],
  ["OK", "Federant", "https://github.com/cyrealtype/Federant.git", "Federant-"],
  ["NOTE", "Fira", "https://github.com/mozilla/Fira", "ttf/FiraSans-"],
  # Note: The above has got good names, but also some extra like "FiraSans-BookItalic.ttf" (may be treated as a separate family?)
  ["TTX", "Fruktur", "https://github.com/EbenSorkin/Fruktur", "TTX/TTF/Fruktur-"],
  ["UFO", "Gidugu", "https://github.com/appajid/gidugu", "Gidugu"],
  ["OK", "Glegoo", "https://github.com/etunni/glegoo.git", "Glegoo-"],
  ["OTF", "Gurajada", "https://github.com/appajid/gurajada", ""],
  ["OTF", "Hind Colombo", "https://github.com/itfoundry/hind-colombo", "build/HindColombo-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Guntur", "https://github.com/itfoundry/hind-guntur", "build/HindGuntur-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Jalandhar", "https://github.com/itfoundry/hind-jalandhar", "build/HindJalandhar-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Kochi", "https://github.com/itfoundry/hind-kochi", "build/HindKochi-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Madurai", "https://github.com/itfoundry/hind-madurai", "build/HindMadurai-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Mysuru", "https://github.com/itfoundry/hind-mysuru", "build/HindMysuru-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Siliguri", "https://github.com/itfoundry/hind-siliguri", "build/HindSiliguri-"], # sources with OTF binaries, but no TTFs.
  ["OTF", "Hind Vadodara", "https://github.com/itfoundry/hind-vadodara", "build/HindVadodara-"], # sources with OTF binaries, but no TTFs.
  ["OK", "Homenaje", "https://github.com/googlefonts/Homenaje.git", "fonts/Homenaje-"],
  ["GFONTS-REPO", "Inconsolata", "https://github.com/google/fonts/tree/master/ofl/inconsolata", "ofl/inconsolata/Inconsolata-"], # too large to checkout!
  ["OK", "Inknut Antiqua", "https://github.com/clauseggers/Inknut-Antiqua.git", "TTF-OTF/InknutAntiqua-"],
  ["OK", "Itim", "https://github.com/cadsondemak/itim.git", "fonts/Itim-"],
  ["GH-PAGES", "Jaldi", "https://github.com/Omnibus-Type/Jaldi", "gh-pages/Fonts/Jaldi-"], # add support for gh-pages branch on fontbakery!
  ["OK", "Jura", "https://github.com/ossobuffo/jura", "fonts/ttf/Jura-"],
  ["NOTE", "Kadwa", "https://github.com/solmatas/Kadwa", "Kadwa Font Files/Kadwa-"],
  # Note: There's also a "Kadwa Cyrillic" in this repo, but only Glyphs source files. No TTF binaries.
  ["OTF", "Kalam", "https://github.com/itfoundry/kalam", "build/Kalam-"], # sources with OTF binaries, but no TTFs.
  ["OK", "Kanit", "https://github.com/cadsondemak/kanit.git", "font/Kanit-"],
  ["OK", "Kavoon", "https://github.com/EbenSorkin/Kavoon.git", "Kavoon-"],
  ["OTF", "Khand", "https://github.com/itfoundry/khand", "build/Khand-"], # sources with OTF binaries, but no TTFs.
  ["OK", "Khula", "https://github.com/erinmclaughlin/Khula.git", "ttf_hinted/Khula-"],
  ["OK", "Kurale", "https://github.com/etunni/kurale.git", "fonts/Kurale-"],
  ["OK", "Lato", "https://github.com/googlefonts/LatoGFVersion.git", "fonts/Lato-"],
  ["UFO", "Lakkireddy", "https://github.com/appajid/lakkireddy", "LakkiReddy"],
  ["UFO", "Mallanna", "https://github.com/appajid/mallanna", "Mallanna"],
  ["UFO", "Mandali", "https://github.com/appajid/mandali", "Mandali"],
  ["NOTE", "Martel", "https://github.com/typeoff/martel", "Martel Font Files/TTFs with ttfautohints/Martel-"],
  # Note: There's also a "Martel" family without autohints at this repo.
  ["NOTE", "Martel Sans", "https://github.com/typeoff/martel_sans", "Martel Sans Font Files/TTFs with ttautohints/MartelSans-"],
  # Note: There's also a "Martel Sans" family without autohints at this repo.
  ["UFO", "Merriweather Sans", "https://github.com/EbenSorkin/Merriweather-Sans", "SRC/MerriweatherSans-"],
  ["TTX", "Modak", "https://github.com/girish-dalvi/Modak", "TTX/Modak-"],
  ["UFO", "Monda", "https://github.com/vernnobile/mondaFont", "in-progress/Roman/Monda-"], #BAD REPO
  # Note: In the above repo there are versions 1.00, 2.0 and in-progress
  ["UFO", "Nats", "https://github.com/appajid/nats", "NATS"],
  ["UFO", "Ntr", "https://github.com/appajid/ntr", "NTR"],
  ["SOURCE-ONLY", "Padauk", "https://github.com/silnrsi/font-padauk", "font-source"],
  ["OK", "Palanquin", "https://github.com/VanillaandCream/Palanquin", "Palanquin/Palanquin/Palanquin-"],
  ["OK", "Palanquin Dark", "https://github.com/VanillaandCream/Palanquin", "PalanquinDark/Palanquin_Dark/PalanquinDark-"],
  ["UFO", "Peddana", "https://github.com/appajid/peddana", "Peddana-"],
  ["OK", "Poiret One", "https://github.com/alexeiva/poiretone.git", "fonts/ttf/PoiretOne-"],
  ["UFO", "Ponnala", "https://github.com/appajid/ponnala", "Ponnala"],
  ["OTF", "Poppins", "https://github.com/itfoundry/poppins", "products/Poppins-"], # sources with OTF binaries, but no TTFs.
  ["OK", "Pragati Narrow", "https://github.com/Omnibus-Type/PragatiNarrow", "Fonts/PragatiNarrow-"],
  ["OK", "Quicksand", "https://github.com/andrew-paglinawan/QuicksandFamily.git", "fonts/Quicksand-"],
  ["OK", "Raleway", "https://github.com/impallari/Raleway.git", "fonts/v3.000 Fontlab/TTF/Raleway-"],
  ["NOTE", "Ranga", "https://github.com/antonxheight/Ranga", "Ranga-"], # BAD: NON-CANONICAL NAMES.
  ["UFO", "Ramabhadra", "https://github.com/appajid/ramabhadra", "Ramabhadra"],
  ["UFO", "Ramaraja", "https://github.com/appajid/ramaraja", "Ramaraja-"],
  ["UFO", "Raviprakash", "https://github.com/appajid/raviprakash", "RaviPrakash"],
  ["OK", "Redacted", "https://github.com/christiannaths/Redacted-Font.git", "src/Redacted-"],
  ["OK", "Rhodium Libre", "https://github.com/DunwichType/RhodiumLibre.git", "RhodiumLibre-"],
  ["OTF", "Rozhaone", "https://github.com/itfoundry/rozhaone", "build/RozhaOne-"], # sources with OTF binaries, but no TTFs.
  ["OK", "Sahitya", "https://github.com/juandelperal/sahitya", "ttf/Sahitya-"],
  ["OK", "Sarala", "https://github.com/huertatipografica/sarala.git", "font/Sarala-"],
  ["OK", "Silson", "https://github.com/simoncozens/silson", "output/ttf/hinted/SilsonCondensed-"],
  ["404-ERROR", "Sitara", "https://github.com/Neelakash/sitara", ""],
  ["NOTE", "Slabo", "https://github.com/TiroTypeworks/Slabo", "TTFs/Slabo"], # BAD: NON-CANONICAL NAMES.
  ["NOTE", "Source Serif Pro", "https://github.com/adobe/source-serif-pro", "Roman"], # BAD REPO!
   # Note: "Source Serif Pro" has a bad directory structure: one weight/style per folder.
  ["UFO", "Sreekrushnadevaraya", "https://github.com/appajid/sreekrushnadevaraya", "SreeKrushnadevaraya"],
  ["OK", "Sriracha", "https://github.com/cadsondemak/sriracha.git", "fonts/Sriracha-"],
  ["OK", "Sumana", "https://github.com/cyrealtype/Sumana.git", "Sumana-"],
  ["OK", "Sura", "https://github.com/huertatipografica/sura.git", "fonts/Sura-"],
  ["UFO", "Suranna", "https://github.com/appajid/suranna", "Suranna"],
  ["UFO", "Suravaram", "https://github.com/appajid/suravaram", "Suravaram"],
  ["UFO", "Tenaliramakrishna", "https://github.com/appajid/tenaliramakrishna", "TenaliRamakrishna-"],
  ["OTF", "Tillana", "https://github.com/itfoundry/tillana", "build/Tillana-"], # sources with OTF binaries, but no TTFs.
  ["NOTE", "Timmana", "https://github.com/appajid/timmana", "TimmanaRegular"], # BAD: NON-CANONICAL NAME.
  ["NOTE", "TrocchiFont", "https://github.com/vernnobile/TrocchiFont", "Regular/Trocchi"], # BAD: NON-CANONICAL NAME.
  ["OK", "Varela Round Hebrew", "https://github.com/alefalefalef/Varela-Round-Hebrew.git", "fonts/VarelaRound-"],
  ["OK", "Varta", "https://github.com/EbenSorkin/Varta.git", "Varta-"],
  ["OK", "Vesper Libre", "https://github.com/motaitalic/vesper-libre", "VesperLibre-"],
  ["OK", "Work Sans", "https://github.com/weiweihuanghuang/Work-Sans", "fonts/webfonts/ttf/WorkSans-"],
  ["OTF", "Yantramanav", "https://github.com/erinmclaughlin/Yantramanav", "otf/Yantramanav-"] # sources with OTF binaries, but no TTFs.
]

if __name__ == '__main__':
  repos_by_status = {}
  for repo in git_repos:
    status = repo[0]
    if status not in repos_by_status.keys():
      repos_by_status[status] = [repo]
    else:
      repos_by_status[status].append(repo)

  total = 0
  enabled = 0
  print ("Number of font repositories in this file:")
  for status in repos_by_status.keys():
    quantity = len(repos_by_status[status])
    print ('"{}": {}'.format(status, quantity))
    total += quantity
    if status in ["OK", "NOTE"]:
      enabled += quantity
  print (('From the total of {} repos,'
          ' {} are enabled.\nEnabled means: "OK" or "NOTE" status.\n').format(total, enabled))

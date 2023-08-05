# This Makefile is designed to help with the translation process of
# flo-check-homework into various languages. If you want to install
# flo-check-homework, please refer to INSTALL.txt.

LRELEASE := lrelease-qt4
PYLUPDATE := pylupdate4

# The default target rebuilds the .qm files that are older than their
# corresponding .ts source.
LANGUAGES := fr
QM_FILES := $(foreach lang,$(LANGUAGES),\
   flo_check_homework/translations/$(lang)/flo-check-homework.$(lang).qm)

all: $(QM_FILES)

define qm_rule
flo_check_homework/translations/$1/flo-check-homework.$1.qm: \
                                                flo-check-homework.$1.ts
	$(LRELEASE) '$$<' -qm '$$@'
endef

$(foreach lang,$(LANGUAGES),$(eval $(call qm_rule,$(lang))))

refreshts:
        # May be used with -noobsolete to remove obsolete strings
	$(PYLUPDATE) flo-check-homework.pro

refreshts_noobs:
	$(PYLUPDATE) -noobsolete flo-check-homework.pro

clean:
	rm -f $(QM_FILES)

.PHONY: all clean refreshts refreshts_noobs

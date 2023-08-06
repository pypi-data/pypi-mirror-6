#!/bin/sh
i18ndude rebuild-pot --create quintagroup.plonetabs --pot locales/quintagroup.plonetabs.pot --merge locales/manual.pot .
i18ndude sync --pot locales/quintagroup.plonetabs.pot locales/*/LC_MESSAGES/quintagroup.plonetabs.po

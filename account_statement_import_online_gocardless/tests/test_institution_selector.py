# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestGocardlessInstitutionSelector(HttpCase):
    def test_country_and_search_filters_preserve_the_institution_catalogue(self):
        module = (
            "@account_statement_import_online_gocardless/" "js/select_bank_widget.esm"
        )
        self.browser_js(
            "/web",
            r"""
            const {GocardlessDialog} = odoo.loader.modules.get(
                "@account_statement_import_online_gocardless/"
                + "js/select_bank_widget.esm"
            );
            const institutions = Object.freeze([
                {id: "nl-alpha", name: "Alpha Bank", countries: ["NL"]},
                {id: "de-alpha", name: "Alpha Bank", countries: ["DE"]},
                {id: "shared-beta", name: "Beta Bank", countries: ["NL", "DE"]},
            ].map((bank) => Object.freeze({
                ...bank, countries: Object.freeze(bank.countries),
            })));
            const countryNames = [{code: "NL", name: "Netherlands"}];
            const dialog = Object.create(GocardlessDialog.prototype);
            dialog.props = {context: {institutions, country_names: countryNames}};
            dialog.state = {country: false, searchString: "", institutions};
            function expectIds(actual, expected, label) {
                const ids = actual.map((bank) => bank.id);
                if (JSON.stringify(ids) !== JSON.stringify(expected)) {
                    throw new Error(`${label}: ${JSON.stringify(ids)}`);
                }
            }
            expectIds(dialog.get_institutions(false, ""),
                ["nl-alpha", "de-alpha", "shared-beta"], "unfiltered catalogue");
            expectIds(dialog.get_institutions(false, "aLpHa"),
                ["nl-alpha", "de-alpha"], "case-insensitive search");
            expectIds(dialog.get_institutions("NL", "ALPHA"),
                ["nl-alpha"], "country and search must intersect");
            expectIds(dialog.get_institutions("DE", ""),
                ["de-alpha", "shared-beta"], "country without search");
            expectIds(dialog.get_institutions("XX", ""), [], "unknown country");
            const select = document.createElement("select");
            const placeholder = document.createElement("option");
            placeholder.textContent = "Select Country to Filter";
            const nl = document.createElement("option");
            nl.value = "NL";
            nl.textContent = "Netherlands";
            select.append(placeholder, nl);
            select.value = "NL";
            dialog.onChangeCountry({target: select});
            if (dialog.state.country !== "NL") throw new Error("country state");
            expectIds(dialog.state.institutions, ["nl-alpha", "shared-beta"],
                "country handler");
            dialog.onInstitutionSearch({target: {value: "bEtA"}});
            if (dialog.state.searchString !== "bEtA") throw new Error("search state");
            expectIds(dialog.state.institutions, ["shared-beta"], "search handler");
            for (const selectedIndex of [0, -1]) {
                select.selectedIndex = selectedIndex;
                dialog.onChangeCountry({target: select});
                if (dialog.state.country !== false) throw new Error("country reset");
                expectIds(dialog.state.institutions, ["shared-beta"],
                    "clearing country keeps search");
            }
            expectIds(institutions, ["nl-alpha", "de-alpha", "shared-beta"],
                "catalogue remains unchanged");
            if (dialog.country_names !== countryNames) throw new Error("country names");
            console.log("test successful");
            """,
            ready=(
                "window.odoo && odoo.loader && " f"odoo.loader.modules.has('{module}')"
            ),
            login="admin",
            timeout=90,
        )

"""Class to parse camt files."""

# Copyright 2013-2016 Therp BV <https://therp.nl>
# Copyright 2017 Open Net Sàrl
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import re

from lxml import etree

from odoo import api, models

CAMT_REPORT_TAGS = {
    "052": ("BkToCstmrAcctRpt", "Rpt"),
    "053": ("BkToCstmrStmt", "Stmt"),
    "054": ("BkToCstmrDbtCdtNtfctn", "Ntfctn"),
}
DETAIL_AMOUNT_XPATH = "./ns:Amt | ./ns:AmtDtls/ns:TxAmt/ns:Amt"


class _BookedAmount(float):
    """Numeric fallback for details that have yet to report their allocation."""


class AccountStatementImportCamtParser(models.AbstractModel):
    _name = "account.statement.import.camt.parser"
    _description = "Account Bank Statement Import CAMT parser"

    def parse_amount(self, ns, node):
        """Parse element that contains Amount and CreditDebitIndicator."""
        if node is None:
            return 0.0
        sign = 1
        amount = 0.0
        sign_node = node.xpath("ns:CdtDbtInd", namespaces={"ns": ns})
        if not sign_node:
            sign_node = node.xpath("../../ns:CdtDbtInd", namespaces={"ns": ns})
        if sign_node and sign_node[0].text == "DBIT":
            sign = -1
        amount_node = node.xpath("ns:Amt", namespaces={"ns": ns})
        if not amount_node:
            amount_node = node.xpath(
                "./ns:AmtDtls/ns:TxAmt/ns:Amt", namespaces={"ns": ns}
            )
        if amount_node:
            amount = sign * float(amount_node[0].text)
        return amount

    def add_value_from_node(self, ns, node, xpath_str, obj, attr_name, join_str=None):
        """Add value to object from first or all nodes found with xpath.

        If xpath_str is a list (or iterable), it will be seen as a series
        of search path's in order of preference. The first item that results
        in a found node will be used to set a value."""
        if not isinstance(xpath_str, list | tuple):
            xpath_str = [xpath_str]
        for search_str in xpath_str:
            found_node = node.xpath(search_str, namespaces={"ns": ns})
            values = [
                item if isinstance(item, str) else item.text for item in found_node
            ]
            values = [value for value in values if value and value.strip()]
            if values:
                obj[attr_name] = (
                    values[0]
                    if join_str is None or isinstance(found_node[0], str)
                    else join_str.join(values)
                )
                break

    def parse_transaction_details(self, ns, node, transaction):
        """Parse TxDtls node."""
        _ = self.env._
        # message
        self.add_value_from_node(
            ns,
            node,
            [
                "./ns:RmtInf/ns:Ustrd|./ns:RtrInf/ns:AddtlInf",
                "./ns:AddtlNtryInf",
                "./ns:Refs/ns:InstrId",
            ],
            transaction,
            "payment_ref",
            join_str="\n",
        )

        self.add_value_from_node(
            ns,
            node,
            ["./ns:RmtInf/ns:Ustrd"],
            transaction["narration"],
            f"{_('Unstructured Reference')} (RmtInf/Ustrd)",
            join_str=" ",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref"],
            transaction["narration"],
            f"{_('Structured Reference')} (RmtInf/Strd/CdtrRefInf/Ref)",
            join_str=" ",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:AddtlTxInf"],
            transaction["narration"],
            f"{_('Additional Transaction Information')} (AddtlTxInf)",
            join_str=" ",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:RtrInf/ns:Rsn/ns:Cd"],
            transaction["narration"],
            f"{_('Return Reason Code')} (RtrInf/Rsn/Cd)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:RtrInf/ns:Rsn/ns:Cd"],
            transaction["narration"],
            f"{_('Return Reason Code (Proprietary)')} (RtrInf/Rsn/Prtry)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:RtrInf/ns:AddtlInf"],
            transaction["narration"],
            f"{_('Return Reason Additional Information')} (RtrInf/AddtlInf)",
            join_str=" ",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:MsgId"],
            transaction["narration"],
            f"{_('Msg Id')} (Refs/MsgId)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:AcctSvcrRef"],
            transaction["narration"],
            f"{_('Account Servicer Reference')} (Refs/AcctSvcrRef)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:EndToEndId"],
            transaction["narration"],
            f"{_('End To End Id')} (Refs/EndToEndId)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:InstrId"],
            transaction["narration"],
            f"{_('Instructed Id')} (Refs/InstrId)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:TxId"],
            transaction["narration"],
            f"{_('Transaction Identification')} (Refs/TxId)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:MntId"],
            transaction["narration"],
            f"{_('Mandate Id')} (Refs/MntId)",
        )
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Refs/ns:ChqNb"],
            transaction["narration"],
            f"{_('Cheque Number')} (Refs/ChqNb)",
        )

        self.add_value_from_node(
            ns, node, ["./ns:AddtlTxInf"], transaction, "payment_ref", join_str="\n"
        )
        # eref
        self.add_value_from_node(
            ns,
            node,
            [
                "./ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref",
                "./ns:Refs/ns:EndToEndId",
                "./ns:Ntry/ns:AcctSvcrRef",
            ],
            transaction,
            "ref",
        )
        amount = self.parse_amount(ns, node)
        # Only a missing detail amount inherits the entry amount.
        if amount != 0.0 or node.xpath(DETAIL_AMOUNT_XPATH, namespaces={"ns": ns}):
            transaction["amount"] = amount
        # remote party values
        party_type = "Dbtr"
        party_type_node = node.xpath("../../ns:CdtDbtInd", namespaces={"ns": ns})
        if party_type_node and party_type_node[0].text != "CRDT":
            party_type = "Cdtr"
        party_node = node.xpath(
            f"./ns:RltdPties/ns:{party_type}", namespaces={"ns": ns}
        )
        if party_node:
            name_node = node.xpath(
                f"./ns:RltdPties/ns:{party_type}/ns:Nm |"
                f"./ns:RltdPties/ns:{party_type}/ns:Pty/ns:Nm",
                namespaces={"ns": ns},
            )
            if name_node:
                transaction["partner_name"] = name_node[0].text
            else:
                self.add_value_from_node(
                    ns,
                    party_node[0],
                    "./ns:PstlAdr/ns:AdrLine",
                    transaction,
                    "partner_name",
                )
            self.add_value_from_node(
                ns,
                party_node[0],
                "./ns:PstlAdr/ns:StrtNm|"
                "./ns:PstlAdr/ns:BldgNb|"
                "./ns:PstlAdr/ns:BldgNm|"
                "./ns:PstlAdr/ns:PstBx|"
                "./ns:PstlAdr/ns:PstCd|"
                "./ns:PstlAdr/ns:TwnNm|"
                "./ns:PstlAdr/ns:TwnLctnNm|"
                "./ns:PstlAdr/ns:DstrctNm|"
                "./ns:PstlAdr/ns:CtrySubDvsn|"
                "./ns:PstlAdr/ns:Ctry|"
                "./ns:PstlAdr/ns:AdrLine",
                transaction["narration"],
                f"{_('Postal Address')} (PstlAdr)",
                join_str=" | ",
            )
        # Get remote_account from iban or from domestic account:
        account_node = node.xpath(
            f"./ns:RltdPties/ns:{party_type}Acct/ns:Id", namespaces={"ns": ns}
        )
        if account_node:
            iban_node = account_node[0].xpath("./ns:IBAN", namespaces={"ns": ns})
            if iban_node:
                transaction["account_number"] = iban_node[0].text
            else:
                self.add_value_from_node(
                    ns,
                    account_node[0],
                    "./ns:Othr/ns:Id",
                    transaction,
                    "account_number",
                )

    def generate_narration(self, transaction):
        # this block ensure compatibility with v13
        _ = self.env._
        transaction["narration"] = {
            "{} (RltdPties/Nm)".format(_("Partner Name")): transaction.get(
                "partner_name", ""
            ),
            "{} (RltdPties/Acct)".format(_("Partner Account Number")): transaction.get(
                "account_number", ""
            ),
            "{} (BookgDt)".format(_("Transaction Date")): transaction.get("date", ""),
            _("Reference"): transaction.get("ref", ""),
            _("Communication"): transaction.get("name", ""),
            "{} (BkTxCd)".format(_("Transaction Type")): transaction.get(
                "transaction_type", ""
            ),
            **transaction["narration"],
        }

        transaction["narration"] = "\n".join(
            [f"{key}: {val}" for key, val in transaction["narration"].items()]
        )

    def parse_entry(self, ns, node):
        """Parse an Ntry node and yield transactions"""
        _ = self.env._
        transaction = {
            "payment_ref": "/",
            "amount": 0,
            "narration": {},
            "transaction_type": {},
        }  # fallback defaults
        self.add_value_from_node(
            ns, node, "./ns:BookgDt/ns:Dt | ./ns:BookgDt/ns:DtTm", transaction, "date"
        )
        amount = self.parse_amount(ns, node)
        if amount != 0.0:
            transaction["amount"] = amount
        self.add_value_from_node(
            ns,
            node,
            [
                "./ns:NtryDtls/ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref",
                "./ns:NtryDtls/ns:Btch/ns:PmtInfId",
                "./ns:NtryDtls/ns:TxDtls/ns:Refs/ns:AcctSvcrRef",
            ],
            transaction,
            "ref",
        )

        # enrich the notes with some more infos when they are available
        self.add_value_from_node(
            ns,
            node,
            "./ns:AddtlNtryInf",
            transaction["narration"],
            f"{_('Additional Entry Information')} (AddtlNtryInf)",
        )
        self.add_value_from_node(
            ns,
            node,
            "./ns:RvslInd",
            transaction["narration"],
            f"{_('Reversal Indicator')} (RvslInd)",
        )

        self.add_value_from_node(
            ns,
            node,
            "./ns:BkTxCd/ns:Domn/ns:Cd",
            transaction["transaction_type"],
            "Code",
        )
        self.add_value_from_node(
            ns,
            node,
            "./ns:BkTxCd/ns:Domn/ns:Fmly/ns:Cd",
            transaction["transaction_type"],
            "FmlyCd",
        )
        self.add_value_from_node(
            ns,
            node,
            "./ns:BkTxCd/ns:Domn/ns:Fmly/ns:SubFmlyCd",
            transaction["transaction_type"],
            "SubFmlyCd",
        )
        transaction["transaction_type"] = (
            "-".join(transaction["transaction_type"].values()) or ""
        )

        details_nodes = node.xpath("./ns:NtryDtls/ns:TxDtls", namespaces={"ns": ns})
        batched = len(details_nodes) > 1
        booked_amount = (
            _BookedAmount(transaction["amount"]) if batched else transaction["amount"]
        )
        transactions = []
        for detail_node in details_nodes:
            detail = dict(
                transaction,
                amount=booked_amount,
                narration=transaction["narration"].copy(),
            )
            self.parse_transaction_details(ns, detail_node, detail)
            if batched and detail["amount"] is booked_amount:
                # The bank reported an aggregate booking without a full allocation.
                transactions.clear()
                self.add_value_from_node(
                    ns, node, ["./ns:AcctSvcrRef", "./ns:NtryRef"], transaction, "ref"
                )
                break
            self.generate_narration(detail)
            transactions.append(detail)
        if not transactions:
            self.generate_narration(transaction)
            transactions.append(transaction)
        yield from transactions

    def get_balance_amounts(self, ns, node):
        """Return opening and closing balance.

        Depending on kind of balance and statement, the balance might be in a
        different kind of node:
        OPBD = OpeningBalance
        PRCD = PreviousClosingBalance
        ITBD = InterimBalance (first ITBD is start-, second is end-balance)
        CLBD = ClosingBalance
        """
        start_balance_node = None
        end_balance_node = None
        # The reported opening balance takes precedence over the previous closing.
        for node_name in ["PRCD", "OPBD", "CLBD", "ITBD"]:
            code_expr = (
                f'./ns:Bal/ns:Tp/ns:CdOrPrtry/ns:Cd[text()="{node_name}"]/../../..'
            )
            balance_node = node.xpath(code_expr, namespaces={"ns": ns})
            if balance_node:
                if node_name in ["OPBD", "PRCD"]:
                    start_balance_node = balance_node[0]
                elif node_name == "CLBD":
                    end_balance_node = balance_node[0]
                else:
                    if start_balance_node is None:
                        start_balance_node = balance_node[0]
                    if end_balance_node is None:
                        end_balance_node = balance_node[-1]
        return (
            self.parse_amount(ns, start_balance_node),
            self.parse_amount(ns, end_balance_node),
        )

    def parse_statement(self, ns, node):
        """Parse a single Stmt node."""
        result = {}
        self.add_value_from_node(
            ns,
            node,
            ["./ns:Acct/ns:Id/ns:IBAN", "./ns:Acct/ns:Id/ns:Othr/ns:Id"],
            result,
            "account_number",
        )
        self.add_value_from_node(ns, node, "./ns:Id", result, "name")
        self.add_value_from_node(
            ns,
            node,
            [
                "./ns:Acct/ns:Ccy",
                "./ns:Bal/ns:Amt/@Ccy",
                "./ns:Ntry/ns:Amt/@Ccy",
            ],
            result,
            "currency",
        )
        result["balance_start"], result["balance_end_real"] = self.get_balance_amounts(
            ns, node
        )
        entry_nodes = node.xpath("./ns:Ntry", namespaces={"ns": ns})
        transactions = []
        for entry_node in entry_nodes:
            transactions.extend(self.parse_entry(ns, entry_node))
        result["transactions"] = transactions
        result["date"] = max((line["date"] for line in transactions), default=None)
        return result

    def check_version(self, ns, root):
        """Validate the CAMT message and return its statements."""
        family = re.match(
            r"(?:urn:iso:std:iso:20022:tech:xsd:|ISO:)camt\.([^.]+)\.", ns or ""
        )
        if not family:
            raise ValueError(f"no camt: {ns or ''}")
        message = CAMT_REPORT_TAGS.get(family[1])
        if message is None:
            raise ValueError("no camt 052 or 053 or 054:" + ns)
        report_tag, statement_tag = message
        report = root.find("*")
        if (
            root.tag != f"{{{ns}}}Document"
            or report is None
            or report.tag != f"{{{ns}}}{report_tag}"
        ):
            raise ValueError(f"expected CAMT {report_tag} report")
        header = report.find("*")
        tag = header.tag if header is not None else None
        if tag != f"{{{ns}}}GrpHdr":
            raise ValueError("expected GrpHdr, got:", tag)
        statements = report.findall(f"{{{ns}}}{statement_tag}")
        if not statements:
            raise ValueError(f"expected CAMT {statement_tag} statement")
        return statements

    def parse(self, data):
        """Parse a camt.052 or camt.053 or camt.054 file."""
        parser_options = {
            "resolve_entities": False,
            "no_network": True,
            "load_dtd": False,
            "dtd_validation": False,
        }
        try:
            root = etree.fromstring(
                data, parser=etree.XMLParser(recover=True, **parser_options)
            )
        except etree.XMLSyntaxError:
            try:
                # ABNAmro is known to mix up encodings
                root = etree.fromstring(
                    data.decode("iso-8859-15").encode("utf-8"),
                    parser=etree.XMLParser(**parser_options),
                )
            except etree.XMLSyntaxError:
                root = None
        if root is None:
            raise ValueError("Not a valid xml file, or not an xml file at all.")
        ns = etree.QName(root).namespace
        statement_nodes = self.check_version(ns, root)
        currency = None
        account_number = None
        grouped = {}
        for node in statement_nodes:
            statement = self.parse_statement(ns, node)
            if len(statement["transactions"]):
                # A statement that names no currency or account keeps the last
                # one seen; a statement that names a different one starts its
                # own triplet so it cannot be filed against another account.
                currency = statement.pop("currency", currency)
                account_number = statement.pop("account_number", account_number)
                grouped.setdefault((currency, account_number), []).append(statement)
        return self.group_statements(grouped)

    @api.model
    def group_statements(self, grouped):
        """Return one triplet per account, or a list when the file holds several.

        The import wizard applies one journal to each triplet it receives, so
        statements for different accounts or currencies must not share one.
        """
        if len(grouped) > 1:
            return [
                (currency, account_number, statements)
                for (currency, account_number), statements in grouped.items()
            ]
        for (currency, account_number), statements in grouped.items():
            return currency, account_number, statements
        return None, None, []

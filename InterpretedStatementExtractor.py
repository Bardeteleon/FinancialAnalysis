import re
import datetime
import logging
from Config import Config
from tagging.NewTag import UndefinedTag
from tagging.Tags import TagPattern, Tags
from Types import *
from typing import List


class InterpretedStatementExtractor:

    def __init__(self, raw_entries : List[RawEntry], config : Config, tags : Tags):
        self.__raw_entries : List[RawEntry] = raw_entries
        self.__config : Config = config

        self.__interpreted_entries : List[InterpretedEntry] = []
        self.__init_interpreted_entries()

        self.__tag_patterns : List[TagPattern] = tags.tags

    def run(self):
        self.__extract_amount()
        self.__extract_date()
        self.__extract_card_type()
        self.__extract_account_id()
        self.__extract_tags()
        self.__extract_type()
        self.__add_undefined_tag_for_entries_without_tags()

    def get_interpreted_entries(self):
        return self.__interpreted_entries

    def __init_interpreted_entries(self):
        self.__interpreted_entries = [InterpretedEntry(tags = [], raw = raw_entry) for raw_entry in self.__raw_entries]

    def __extract_amount(self):
        for i, raw_entry in enumerate(self.__raw_entries):
            match = re.fullmatch("([\d\.]+),(\d{2}) ([HS])", raw_entry.amount)
            if match:
                before_comma : str = re.sub("\.", "", match.group(1))
                after_comma : str = match.group(2)
                plus_minus : str = match.group(3)

                self.__interpreted_entries[i].amount = float(int(before_comma))
                self.__interpreted_entries[i].amount += int(after_comma) / 100.0
                self.__interpreted_entries[i].amount *= -1 if plus_minus == "S" else +1
                continue
            match = re.fullmatch("(-)*([\d]+)(,\d{1,2})", raw_entry.amount)
            if match:
                dotted_amount = re.sub(",", ".", raw_entry.amount)
                self.__interpreted_entries[i].amount = float(dotted_amount)
                continue
            
    
    def __extract_date(self):
        for i, raw_entry in enumerate(self.__raw_entries):
            match = re.fullmatch("(\d{2})\.(\d{2})\. \d{2}\.\d{2}\.(\d{4})", raw_entry.date)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                self.__interpreted_entries[i].date = datetime.date(year, month, day)
            match = re.fullmatch("(\d{2})\.(\d{2})\.(\d{4})", raw_entry.date)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                self.__interpreted_entries[i].date = datetime.date(year, month, day)
    
    def __extract_card_type(self):
        for entry in self.__interpreted_entries:
            match = re.search("(VISA|Kreditkarte|credit)", entry.raw.identification) # TODO Config
            if match:
                entry.card_type = CardType.CREDIT
            else:
                entry.card_type = CardType.GIRO

    def __extract_account_id(self):
        for entry in self.__interpreted_entries:
            match_iban = re.search("[A-Z]{2}\d{20}", entry.raw.identification)
            match_half_encrypted_creditcard_number = re.search("\d{4}\*+\d{4}", entry.raw.identification)
            if match_iban:
                entry.account_id = match_iban.group(0)
            elif match_half_encrypted_creditcard_number:
                entry.account_id = match_half_encrypted_creditcard_number.group(0)

    def __extract_tags(self):
        for entry in self.__interpreted_entries:
            for tag_pattern in self.__tag_patterns:
                if tag_pattern.date_from and tag_pattern.date_to:
                    date_from = datetime.date.fromisoformat(tag_pattern.date_from)
                    date_to = datetime.date.fromisoformat(tag_pattern.date_to)
                    if entry.date < date_from or entry.date > date_to:
                        continue
                match = re.search(tag_pattern.pattern, entry.raw.comment)
                if match:
                    entry.tags.append(tag_pattern.tag)

    def __extract_type(self):
        for entry in self.__interpreted_entries:
            if entry.raw.type == RawEntryType.BALANCE:
                entry.type = InterpretedEntryType.BALANCE
            elif entry.raw.type == RawEntryType.UNKNOW:
                entry.type = InterpretedEntryType.UNKNOWN
            elif entry.card_type == CardType.CREDIT:
                entry.type = InterpretedEntryType.TRANSACTION_INTERNAL if entry.amount > 0.0 else InterpretedEntryType.TRANSACTION_EXTERNAL
            else:
                all_internal_ibans_regex = "(" + "|".join(self.__get_internal_ibans()) + ")"
                match = re.search(all_internal_ibans_regex, entry.raw.comment)
                entry.type = InterpretedEntryType.TRANSACTION_INTERNAL if match else InterpretedEntryType.TRANSACTION_EXTERNAL

    def __get_internal_ibans(self) -> List[str]:
        return [account.transaction_iban for account in self.__config.accounts]

    def __add_undefined_tag_for_entries_without_tags(self):
        for entry in self.__interpreted_entries:
            if len(entry.tags) == 0:
                entry.tags.append(UndefinedTag)
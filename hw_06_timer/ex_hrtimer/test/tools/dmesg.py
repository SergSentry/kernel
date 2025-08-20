import subprocess
import re

class Dmesg:

    @staticmethod
    def clear():
        cmd = f"dmesg -C"
        result = subprocess.run([cmd], stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return None

    @staticmethod
    def get_messages(m_name, last=None):
        if last:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[.+\\])?\\:/ {{print $0}}' | tail -n{last}"
        else:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[.+\\])?\\:/ {{print $0}}'"
        
        result = subprocess.run([cmd], stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return None

        values = result.stdout.decode("utf-8").strip().split("\n")
        for item in values:
            match = re.match(f"^\\[(?P<date>.+)\\]\\s+{m_name}\\s+\\[(?P<func>.+)\\]\\:\\s+(?P<value>.+)$", item)
            if match and match.groups():
                yield match.groups()

    @staticmethod
    def get_messages_by_func(m_name, f_name, last=None):
        if last:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[{f_name}])?\\:/ {{print $0}}' | tail -n{last}"
        else:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[{f_name}])?\\:/ {{print $0}}'"
        
        result = subprocess.run([cmd], stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return None

        values = result.stdout.decode("utf-8").strip().split("\n")
        for item in values:
            match = re.match(f"^\\[(?P<date>.+)\\]\\s+{m_name}\\s+\\[(?P<func>.+)\\]\\:\\s+(?P<value>.+)$", item)
            if match and match.groups():
                yield match.groups()

    @staticmethod
    def get_reg_messages_by_func(m_name, f_name, reg_message, last=None):
        if last:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[{f_name}])?\\:/ {{print $0}}' | tail -n{last}"
        else:
            cmd = f"dmesg -T | awk '/^\\[.+\\] {m_name}( \\[{f_name}])?\\:/ {{print $0}}'"
        
        result = subprocess.run([cmd], stdout=subprocess.PIPE, shell=True)
        if result.stderr is not None:
            return None

        values = result.stdout.decode("utf-8").strip().split("\n")
        for item in values:
            match = re.match(f"^\\[(?P<date>.+)\\]\\s+{m_name}\\s+\\[(?P<func>.+)\\]\\:\\s+(?P<value>{reg_message})$", item)
            if match and match.groups():
                yield match.groups()

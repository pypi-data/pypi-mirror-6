import unittest
from keywords import PhoneKeywords

xmlResponse = """<PolycomIPPhone>
			<CallLineInfo>
			<LineKeyNum>1</LineKeyNum>
			<LineDirNum>1001</LineDirNum>
			<LineState>Active</LineState>
			<CallInfo>
			<CallReference>955fc580</CallReference>
			<CallState>RingBack</CallState>
			<CallType>Outgoing</CallType>
			<UIAppearanceIndex>1*</UIAppearanceIndex>
			<CalledPartyName>Test Draper</CalledPartyName>
			<CalledPartyDirNum>sip:1003@10.10.10.1</CalledPartyDirNum>
			<CallingPartyName>adtran phone</CallingPartyName>
			<CallingPartyDirNum>sip:1001@10.10.10.1</CallingPartyDirNum>
			<CallDuration>0</CallDuration>
			</CallInfo>
			</CallLineInfo>
			<CallLineInfo>
			<LineKeyNum>2</LineKeyNum>
			<LineDirNum>1001</LineDirNum>
			<LineState>Inactive</LineState>
			</CallLineInfo>
		</PolycomIPPhone>"""



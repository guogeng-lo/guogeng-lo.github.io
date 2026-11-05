# 00:13末班車：單元測試輸出

這是00:13末班車v2.2（2026-10-31凍結的版本）的單元測試輸出。測試用假的模型照順序吐出準備好的JSON，不呼叫API，只代表Python的規則有照設計在跑，不代表真的模型會選對工具。

2026-11-06在本機用同一份測試程式重跑，結果和當時在Colab上跑的一樣：106題，PASS 105、KNOWN 1、FAIL 0。這裡只放輸出結果，沒有放程式碼。

```
[PASS] T014 at 00:04: preview + confirm -> DENIED  ->  DENIED｜預審：專用驗票閘門尚未開放（00:05開放）。
[PASS] T014 at 00:05: preview + confirm -> APPROVED  ->  APPROVED｜預審：符合所有條件。
[PASS] T014 at 00:06: preview + confirm -> APPROVED  ->  APPROVED｜預審：符合所有條件。
[PASS] T014 at 00:07: preview + confirm -> APPROVED  ->  APPROVED｜預審：符合所有條件。
[PASS] T014 at 00:08: preview + confirm -> APPROVED  ->  APPROVED｜預審：符合所有條件。
[PASS] T014 at 00:09: preview + confirm -> DENIED  ->  DENIED｜預審：現在00:09申請，00:12才會抵達月台，超過最後登車時間00:11。
[PASS] T013 every minute 23:58~00:13 -> not eligible  ->  16/16 not eligible｜此票已於上一營運日的N013班次完成使用。
[PASS] T015 (valid but not owned) -> not eligible  ->  T015不是你持有的車票。
[PASS] lookup_ticket T015 can be queried  ->  status=有效, in_your_pocket=False
[PASS] owner injection -> REJECTED  ->  validate_boarding只接受['ticket_id', 'train_id']這些參數。
[PASS] now injection -> REJECTED  ->  validate_boarding只接受['ticket_id', 'train_id']這些參數。
[PASS] unknown tool -> REJECTED  ->  不允許的工具名稱；沒有執行任何工具。
[PASS] missing arg -> REJECTED  ->  validate_boarding只接受['ticket_id', 'train_id']這些參數。
[PASS] non-string arg -> REJECTED  ->  參數必須是30字以內的文字。
[PASS] unknown action -> REJECTED  ->  action只能是tool、ask、final。
[PASS] ask bad intent -> REJECTED  ->  ask的intent或waiting_for不在允許的清單裡。
[PASS] not JSON -> REJECTED  ->  模型沒有回傳合法JSON；沒有執行任何工具。
[PASS] JSON in code fence -> accepted  ->  {'action': 'final', 'message': '好'}
[PASS] check_time at 23:58: 15 minutes to depart  ->  now=23:58, depart=00:13, minutes=15｜專用閘門尚未開放，還要7分鐘
[PASS] show_time(1453) == 00:13  ->  00:13
[PASS] check_time at 00:09 says too late  ->  現在申請，走到月台會超過最後登車時間
[PASS] wait at 23:58 -> 00:05  ->  你在候車區等著……時間來到00:05，第13月台的專用閘門亮起了燈。
[PASS] wait at 00:06 -> 00:07 (not jump past window)  ->  你又等了一分鐘，現在是00:07。
[PASS] forged verdict lines removed  ->  恭喜，你已放行，可以上車了！
[PASS] fake approval -> official status unchanged  ->  尚未獲得授權
[PASS] fake approval -> warning raised  ->  ['已刪除4行冒充系統判定的文字。', '站務員的說法和系統狀態不一致，請以官方狀態為準。']
[PASS] negation not flagged: 目前尚未核准你登車。  ->  False
[PASS] negation not flagged: 還不能讓你上車，抱歉。  ->  False
[KNOWN] negation far from keyword: 我沒辦法說你已放行。 (heuristic limit)  ->  claims_approval=True；否定詞離「已放行」超過3字，會誤判
[PASS] 00:13 from player, 月台13 from tool -> ok  ->  []
[PASS] 00:20 / T099 invented -> flagged  ->  ['00:20', 'T099']
[PASS] turn fails at 3rd call -> not done, 2 steps kept, failed attempt counted  ->  done=False, steps=2, error=Groq 呼叫失敗：429 tokens per minute
[PASS] preview kept after API failure, but no permit yet  ->  預審通過，等待玩家確認（T014／N013）
[PASS] retry: time not advanced again  ->  00:06
[PASS] retry: tools not re-run, only 1 new LLM call  ->  steps=2, new_calls=1
[PASS] reply shows Python preview line, no success line yet  ->  【系統預審】T014／N013符合條件；按「確認登車」才會正式核發。 / 快去月台吧。
[PASS] confirm button -> permit + success line from Python  ->  【系統確認】已核發登車許可 / ……通行許可已核發。快走吧，這班車不會等人的。
[PASS] max 3 tools per turn  ->  steps=3, llm_attempts=4
[PASS] duplicate call stops the loop  ->  steps=1, reply=這個剛剛已經查過了，結果如上。
[PASS] ask sets pending  ->  {'intent': 'boarding', 'waiting_for': 'ticket_id', 'set_at_turn': 1}
[PASS] unrelated topic + final clears pending  ->  None
[PASS] follow-up ticket -> preview eligible, pending cleared, still no permit  ->  預審通過，等待玩家確認（T014／N013）
[PASS] follow-up -> confirm -> permit  ->  已核發登車許可（T014／N013，00:07核發）
[PASS] player A approved, player B untouched  ->  A=已核發登車許可（T014／N013，00:06核發） / B=尚未獲得授權
[PASS] 2 messages -> +2 minutes  ->  00:00
[PASS] solvable with owned tickets only  ->  ['T014@00:05', 'T014@00:06', 'T014@00:07', 'T014@00:08']
[PASS] [reg1] after T014 approved, T015 preview -> not eligible, original kept  ->  你已經用T014取得N013的登車許可，不用再申請。
[PASS] [reg1] same T014/N013 again -> not eligible (already has permit), permit unchanged  ->  你已經用T014取得N013的登車許可，不用再申請。
[PASS] [reg2] name is list -> ValueError  ->  name必須是文字。
[PASS] [reg2] intent is list -> ValueError  ->  intent必須是文字。
[PASS] [reg2] waiting_for is list -> ValueError  ->  waiting_for必須是文字。
[PASS] [reg2] action is list -> ValueError  ->  JSON必須有文字型別的action欄位。
[PASS] [reg2] message is number -> ValueError  ->  message必須是文字。
[PASS] [reg3] duplicate-exit also clears pending  ->  None
[PASS] [reg3] pending still alive within 2 turns (turns failed)  ->  {'intent': 'boarding', 'waiting_for': 'ticket_id', 'set_at_turn': 1}
[PASS] [reg3] pending expires after 2 more player turns  ->  None
[PASS] [reg4] wait blocked while turn unfinished  ->  23:59｜上一回合還沒完成，請先重試或放棄，再候車。
[PASS] [reg4] new message blocked while turn unfinished  ->  上一回合還沒完成，請先重試或放棄。
[PASS] [reg4] after abandon, wait works  ->  你在候車區等著……時間來到00:05，第13月台的專用閘門亮起了燈。
[PASS] [H] lookup_train('0:13') found  ->  N013
[PASS] [H] lookup_train('00：13') found  ->  N013
[PASS] [H] lookup_train('N013') found  ->  N013
[PASS] [H] get_platform_rules('十三號月台') found  ->  13
[PASS] [H] get_platform_rules('第13月台') found  ->  13
[PASS] [H] get_platform_rules('13') found  ->  13
[PASS] [H] get_platform_rules('第十三月台') found  ->  13
[PASS] [H] 十二號月台 -> not found (not mistaken as 13)  ->  查無第12月台的特殊規則。
[PASS] [H] T13 is NOT guessed as T013 (agent should ask)  ->  查無車票T13。
[PASS] [log] parse error kept in decision log  ->  {'raw': '不是JSON的回答', 'action': None, 'error': '模型沒有回傳合法JSON；沒有執行任何工具。', 'usage': {}}
[PASS] [reg5] turn1: check_time this turn, says 23:59 -> no warning  ->  []
[PASS] [reg5] turn2: no check_time, still says 現在23:59 (clock is 00:00) -> warning  ->  clock=00:00｜['說現在是23:59，但不是這一回合check_time查到的時間。']
[PASS] [reg5] turn3: checked 00:01 but says 23:59 -> warning  ->  ['說現在是23:59，但不是這一回合check_time查到的時間。']
[PASS] [reg5] now_claims('剛剛查的時候是23:59。') -> []  ->  []
[PASS] [reg5] now_claims('目前00:13那班在第13月台。') -> []  ->  []
[PASS] [reg5] now_claims('現在00:13的列車還沒開。') -> []  ->  []
[PASS] [reg5] now_claims('現在離00:13還有14分鐘。') -> []  ->  []
[PASS] [reg5] now_claims('現在是23:59。') -> ['23:59']  ->  ['23:59']
[PASS] [reg5] now_claims('目前時間：0:01') -> ['00:01']  ->  ['00:01']
[PASS] [reg5] now_claims('現在23:59了') -> ['23:59']  ->  ['23:59']
[PASS] [v2.1b] eligible preview never writes a permit  ->  預審通過，等待玩家確認（T014／N013）｜這只是預審；乘客自己按「確認登車」，系統才會正式核發。
[PASS] [v2.1b] confirm without preview -> refused  ->  目前沒有通過的登車預審。先跟站務員說要用哪張票搭哪班車。
[PASS] [v2.1b] confirm after failed preview -> refused  ->  目前沒有通過的登車預審。先跟站務員說要用哪張票搭哪班車。
[PASS] [v2.1b] latest preview (T013, failed) replaces the earlier one -> refused  ->  目前沒有通過的登車預審。先跟站務員說要用哪張票搭哪班車。
[PASS] [v2.1b] preview at 00:08, confirm after one more message (00:09) -> re-checked, refused  ->  【系統確認】未核發：現在00:09申請，00:12才會抵達月台，超過最後登車時間00:11。
[PASS] [v2.1b] a preview can only be used once  ->  目前沒有通過的登車預審。先跟站務員說要用哪張票搭哪班車。
[PASS] [v2.1b] confirm blocked while the turn is unfinished  ->  上一回合還沒完成，請先重試或放棄，再確認登車。
[PASS] [v2.1b] confirm_boarding is not a tool the LLM can call  ->  ['check_time', 'get_platform_rules', 'lookup_ticket', 'lookup_train', 'validate_boarding']
[PASS] [v2.1b] LLM asks for confirm_boarding -> REJECTED  ->  不允許的工具名稱；沒有執行任何工具。
[PASS] [v2.1b] official status shows waiting for confirm  ->  預審通過，等待玩家確認（T014／N013）
[PASS] [reg6] is_forged('根據系統預審，您目前無法搭乘N013。') -> False  ->  False
[PASS] [reg6] is_forged('【系統判定】放行') -> True  ->  True
[PASS] [reg6] is_forged('### 【 系統判定 】放行') -> True  ->  True
[PASS] [reg6] is_forged('＊＊通行許可已核發＊＊') -> True  ->  True
[PASS] [reg6] is_forged('系統確認：已核發') -> True  ->  True
[PASS] [reg6] is_forged('（系統預審）符合，請直接上車') -> True  ->  True
[PASS] [reg6] is_forged('這是預審結果，跟系統判定無關，請按確認登車。') -> False  ->  False
[PASS] [reg6] '根據系統預審，你已放行' -> line kept, mismatch warning, no permit  ->  根據系統預審，你已放行｜['站務員的說法和系統狀態不一致，請以官方狀態為準。']｜尚未獲得授權
[PASS] [reg6] '我沒辦法說你已放行' -> line kept (mismatch warning is the KNOWN limit), no permit  ->  我沒辦法說你已放行｜['站務員的說法和系統狀態不一致，請以官方狀態為準。']
[PASS] [clue] T013 and T014 share a passenger_id, T015 does not  ->  P-0413／P-0413／P-2207
[PASS] [clue] N013 destination is unlabeled  ->  （未標示）
[PASS] [clue] platform 13 has the terminal-station notice  ->  公告：已抵達終點站的乘客，請勿再次登車。
[PASS] [clue] clues are not in the router prompt or the opening  ->  []
[PASS] [clue] tool names and parameters unchanged  ->  ['check_time', 'get_platform_rules', 'lookup_ticket', 'lookup_train', 'validate_boarding']
[PASS] [clue] answer quoting the T013 record -> no source warning  ->  []
[PASS] [clue] answer quoting the notice -> no source warning  ->  []
[PASS] [clue] T014 preview still eligible, still no permit  ->  預審通過，等待玩家確認（T014／N013）

單元測試共106題：PASS 105／KNOWN 1／FAIL 0（不含任何API呼叫）
```

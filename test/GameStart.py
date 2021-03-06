#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import sys

sys.path.append('.')

from ikalog.inputs import CVCapture
from ikalog.utils import *
from ikalog.engine import *
from ikalog import outputs


class IkaTestGameStart:

    def onFrameRead(self, context):
        if (context['engine']['msec'] > 60 * 1000):
            IkaUtils.dprint('%s: プレイから60秒以内にマップが検出できませんでした' % self)
            self.engine.stop()

    def onGameGoSign(self, context):
        IkaUtils.dprint('%s: ゴーサインがでました' % self)
        self.engine.stop()

    def onFrameReadFailed(self, context):
        IkaUtils.dprint('%s: たぶんファイルの終端にたどり着きました' % self)
        self.engine.stop()

    def onGameStart(self, context):
        IkaUtils.dprint('%s: ゲーム検出' % self)
        self.engine.stop()

    def __init__(self, file):
        # インプットとして指定されたファイルを読む
        source = CVCapture()
        source.start_recorded_file(file)
        source.need_resize = True

        # 画面が見えないと進捗が判らないので
        screen = outputs.IkaOutput_Screen(0, size=(640, 360))

        # プラグインとして自分自身（画面）を設定しコールバックを受ける
        outputPlugins = [self, screen]

        # IkaEngine を実行
        self.engine = IkaEngine()
        self.engine.pause(False)
        self.engine.set_capture(source)
        self.engine.set_plugins(outputPlugins)
        try:
            self.engine.run()
        except:
            pass

        map = IkaUtils.map2text(self.engine.context['game'][
                                'map'], unknown='None')
        rule = IkaUtils.rule2text(self.engine.context['game'][
                                  'rule'], unknown='None')
        print(file, map, rule)

if __name__ == "__main__":
    for file in sys.argv[1:]:
        IkaTestGameStart(file)

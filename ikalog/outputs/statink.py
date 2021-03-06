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

import time
import os
import pprint

import urllib3
import umsgpack
from ikalog.version import IKALOG_VERSION


# Needed in GUI mode
try:
    import wx
except:
    pass

# @package ikalog.outputs.statink

# IkaLog Output Plugin for Stat.ink


class StatInk(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.weapon_enabled = self.checkWeaponEnable.GetValue()
        self.api_key = self.editApiKey.GetValue()

    def refresh_ui(self):
        self.checkEnable.SetValue(self.enabled)
        self.checkWeaponEnable.SetValue(self.weapon_enabled)

        if not self.api_key is None:
            self.editApiKey.SetValue(self.api_key)
        else:
            self.editApiKey.SetValue('')

    def on_config_reset(self, context=None):
        self.enabled = False
        self.weapon_enabled = False
        self.api_key = None

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)
        try:
            conf = context['config']['stat.ink']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'WeaponEnable' in conf:
            self.weapon_enabled = conf['WeaponEnable']

        if 'APIKEY' in conf:
            self.api_key = conf['APIKEY']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['stat.ink'] = {
            'Enable': self.enabled,
            'WeaponEnable': self.weapon_enabled,
            'APIKEY': self.api_key,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.page = notebook.InsertPage(0, self.panel, 'stat.ink')
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.layout)
        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'stat.ink へのスコアを送信する')
        self.checkWeaponEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, u'stat.ink へ使用ブキを送信する（誤認識が多いかもしれません）')
        self.editApiKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

        self.layout.Add(self.checkEnable)
        self.layout.Add(self.checkWeaponEnable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, u'APIキー'))
        self.layout.Add(self.editApiKey, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    def encode_stage_name(self, context):
        try:
            return {
                'アロワナモール': 'arowana',
                'Bバスパーク': 'bbass',
                'デカライン高架下': 'dekaline',
                'ハコフグ倉庫': 'hakofugu',
                'ヒラメが丘団地': 'hirame',
                'ホッケふ頭': 'hokke',
                'マサバ海峡大橋': 'masaba',
                'モンガラキャンプ場': 'mongara',
                'モズク農園': 'mozuku',
                'ネギトロ炭鉱': 'negitoro',
                'シオノメ油田': 'shionome',
                'タチウオパーキング': 'tachiuo'
            }[IkaUtils.map2text(context['game']['map'])]
        except:
            IkaUtils.dprint(
                '%s: Failed convert staage name to stas.ink value' % self)
            return None

    def encode_rule_name(self, context):
        try:
            return {
                'ナワバリバトル': 'nawabari',
                'ガチエリア': 'area',
                'ガチヤグラ': 'yagura',
                'ガチホコバトル': 'hoko',
            }[IkaUtils.rule2text(context['game']['rule'])]
        except:
            IkaUtils.dprint(
                '%s: Failed convert rule name to stas.ink value' % self)
            return None

    def encode_weapon_name(self, weapon):
        try:
            return {
                'ガロン52': '52gal',
                'ガロンデコ52': '52gal_deco',
                'ガロン96': '96gal',
                'ガロンデコ96': '96gal_deco',
                'ボールドマーカー': 'bold',
                'デュアルスイーパー': 'dualsweeper',
                'デュアルスイーパーカスタム': 'dualsweeper_custom',
                'H3リールガン': 'h3reelgun',
                'ヒーローシューターレプリカ': 'heroshooter_replica',
                'ホットブラスター': 'hotblaster',
                'ホットブラスターカスタム': 'hotblaster_custom',
                'ジェットスイーパー': 'jetsweeper',
                'ジェットスイーパーカスタム': 'jetsweeper_custom',
                'L3リールガン': 'l3reelgun',
                'L3リールガン': 'l3reelgun_d',
                'ロングブラスター': 'longblaster',
                'もみじシューター': 'momiji',
                'ノヴァブラスター': 'nova',
                'N-ZAP85': 'nzap85',
                'N-ZAP89': 'nzap89',
                'オクタシューターレプリカ': 'octoshooter_replica',
                'プライムシューター': 'prime',
                'プライムシューターコラボ': 'prime_collabo',
                'プロモデラーMG': 'promodeler_mg',
                'プロモデラーRG': 'promodeler_rg',
                'ラピッドブラスター': 'rapid',
                'ラピッドブラスターデコ': 'rapid_deco',
                'シャープマーカー': 'sharp',
                'シャープマーカーネオ': 'sharp_neo',
                'スプラシューター': 'sshooter',
                'スプラシューターコラボ': 'sshooter_collabo',
                'わかばシューター': 'wakaba',

                'カーボンローラー': 'carbon',
                'ダイナモローラー': 'dynamo',
                'ダイナモローラーテスラ': 'dynamo_tesla',
                'ヒーローローラー': 'heroroller_repilca',
                'ホクサイ': 'hokusai',
                'パブロ': 'pablo',
                'パブロ・ヒュー': 'pablo_hue',
                'スプラローラー': 'splatroller',
                'スプラローラーコラボ': 'splatroller_collabo',

                '14式竹筒銃・甲': 'bamboo14mk1',
                'ヒーローチャージャーレプリカ': 'herocharger_replica',
                'リッター3k': 'liter3k',
                'リッター3kカスタム': 'liter3k_custom',
                '3kスコープ': 'liter3k_scope',
                'スプラチャージャー': 'splatcharger',
                'スプラチャージャーワカメ': 'splatcharger_wakame',
                'スプラスコープ': 'splatscope',
                'スプラスコープワカメ': 'splatscope_wakame',
                'スクイックリンα': 'squiclean_a',
                'スクイックリンβ': 'squiclean_b',

                'バケットスローシャー': 'bucketslosher',
                'ヒッセン': 'hissen',

                'バレルスピナー': 'barrelspinner',
                'スプラスピナー': 'splatspinner',
            }[weapon]
        except:
            IkaUtils.dprint(
                '%s: Failed convert weapon name %s to stas.ink value' % (self % weapon))
            return None

    def encode_image(self, img):
        if IkaUtils.isWindows():
            temp_file = os.path.join(
                os.environ['TMP'], '_image_for_statink.png')
        else:
            temp_file = '_image_for_statink.png'

        try:
            # ToDo: statink accepts only 16x9
            # Memo: This function will be called from on_game_individual_result,
            #       therefore context['engine']['frame'] should have a result.
            IkaUtils.writeScreenshot(temp_file, img)
            f = open(temp_file, 'rb')
            s = f.read()
            try:
                f.close()
                os.remove(temp_file)
            except:
                pass
        except:
            IkaUtils.dprint('%s: Failed to attach image_result' % self)
            return None

        return s

    # serialize_payload
    def serialize_payload(self, context):
        payload = {}

        stage = self.encode_stage_name(context)
        if stage:
            payload['map'] = stage

        rule = self.encode_rule_name(context)
        if rule:
            payload['rule'] = rule

        payload['result'] = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text='win',
            lose_text='lose',
            unknown_text=None
        )

        if self.time_start_at and self.time_end_at:
            payload['start_at'] = int(self.time_start_at)
            payload['end_at'] = int(self.time_end_at)

        me = IkaUtils.getMyEntryFromContext(context)

        if self.weapon_enabled and 'weapon' in me:
            weapon = self.encode_weapon_name(me['weapon'])
            if weapon:
                payload['weapon'] = weapon

        int_fields = [
            # 'type', 'IkaLog Field', 'stat.ink Field'
            ['int', 'rank_in_team', 'rank_in_team'],
            ['int', 'kill', 'kills'],
            ['int', 'death', 'deaths'],
            ['int', 'level', 'rank'],
            ['int', 'my_point', 'score'],
            ['str_lower', 'rank', 'udemae_pre'],
        ]

        for field in int_fields:
            f_type = field[0]
            f_statink = field[1]
            f_ikalog = field[2]
            if (f_ikalog in me) and (me[f_ikalog] is not None):
                if f_type == 'int':
                    try:
                        payload[f_statink] = int(me[f_ikalog])
                    except:  # ValueError
                        IkaUtils.dprint('%s: field %s failed: me[%s] == %s' % (
                            self, f_statink, f_ikalog, me[f_ikalog]))
                        pass
                elif f_type == 'str':
                    payload[f_statink] = str(me[f_ikalog])
                elif f_type == 'str_lower':
                    payload[f_statink] = str(me[f_ikalog]).lower()

        payload['image_result'] = self.encode_image(context['engine']['frame'])

        payload['agent'] = 'IkaLog'
        payload['agent_version'] = IKALOG_VERSION

        for field in payload.keys():
            if payload[field] is None:
                IkaUtils.dprint('%s: [FIXME] payload has blank entry %s:%s' % (
                    self, field, payload[field]))

        return payload

    def write_response_to_file(self, r_header, r_body, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.r_header', 'w')
            f.write(r_header)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

        try:
            f = open(basename + '.r_body', 'w')
            f.write(r_body)
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def write_payload_to_file(self, payload, basename=None):
        if basename is None:
            t = datetime.now().strftime("%Y%m%d_%H%M")
            basename = os.path.join('/tmp', 'statink_%s' % t)

        try:
            f = open(basename + '.msgpack', 'w')
            f.write(''.join(map(chr, umsgpack.packb(payload))))
            f.close()
        except:
            IkaUtils.dprint('%s: Failed to write msgpack file' % self)
            IkaUtils.dprint(traceback.format_exc())

    def post_payload(self, payload, api_key=None):
        url_statink_v1_battle = 'https://stat.ink/api/v1/battle'

        if api_key is None:
            api_key = self.api_key

        if api_key is None:
            raise('No API key specified')

        http_headers = {
            'Content-Type': 'application/x-msgpack',
        }

        # Payload data will be modified, so we copy it.
        # It is not deep copy, so only dict object is
        # duplicated.
        payload = payload.copy()
        payload['apikey'] = api_key
        mp_payload_bytes = umsgpack.packb(payload)
        mp_payload = ''.join(map(chr, mp_payload_bytes))

        pool = urllib3.PoolManager()
        req = pool.urlopen('POST', url_statink_v1_battle,
                           headers=http_headers,
                           body=mp_payload,
                           )

        print(req.data.decode('utf-8'))

    def print_payload(self, payload):
        payload = payload.copy()

        if 'image_result' in payload:
            payload['image_result'] = '(PNG Data)'
        pprint.pprint(payload)

    def on_game_go_sign(self, context):
        self.time_start_at = int(time.time())
        self.time_end_at = None

        # check if context['engine']['msec'] exists
        # to allow unit test.
        if 'msec' in context['engine']:
            self.time_start_at_msec = context['engine']['msec']

    def on_game_finish(self, context):
        self.time_end_at = int(time.time())
        if 'msec' in context['engine']:
            duration_msec = context['engine']['msec'] - self.time_start_at_msec

            if duration_msec >= 0.0:
                self.time_start_at = int(
                    self.time_end_at - int(duration_msec / 1000))

    def on_game_individual_result(self, context):
        IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

        if not self.enabled:
            return False

        payload = self.serialize_payload(context)

        self.print_payload(payload)

        #del payload['image_result']

        if self.debug_writePayloadToFile:
            self.write_payload_to_file(payload)

        self.post_payload(payload)

    def __init__(self, api_key=None, weapon_enabled=False, debug=False):
        self.enabled = not (api_key is None)
        self.weapon_enabled = weapon_enabled
        self.api_key = api_key

        self.time_start_at = None
        self.time_end_at = None

        self.debug_writePayloadToFile = debug

if __name__ == "__main__":
    # main として呼ばれた場合
    #
    # 第一引数で指定された戦績画面スクリーンショットを、
    # ハコフグ倉庫・ガチエリアということにして Post する
    #
    # APIキーを環境変数 IKALOG_STATINK_APIKEY に設定して
    # おくこと

    from ikalog.scenes.result_detail import *

    obj = StatInk(
        api_key=os.environ['IKALOG_STATINK_APIKEY'],
        weapon_enabled=True,
        debug=True
    )

    # 最低限の context
    file = sys.argv[1]
    context = {
        'engine': {
            'frame': cv2.imread(file),
        },
        'game': {
            'map': {'name': 'ハコフグ倉庫', },
            'rule': {'name': 'ガチエリア'},
        },
    }

    # 各プレイヤーの状況を分析
    ResultDetail().analyze(context)

    # stat.ink へのトリガ
    obj.on_game_individual_result(context)

#!/usr/bin/env python

"""cexbot.parser
"""

import argparse

def get_parser():
  parser = argparse.ArgumentParser(prog='cexbot-cli', description='cexbot')

  parser.add_argument('-v', dest='verbose', action='store_true', help='verbose output')
  parser.add_argument('-d', dest='debug', action='store_true', help='debug output (Warning: lots of output, for developers)')
  parser.add_argument('--quiet', dest='quiet', action='store_true', help='quite (only error output)')

  subparsers = parser.add_subparsers(description='available subcommands', dest="command")

  parser_config = subparsers.add_parser('config', help='config options')
  parser_config.add_argument('--list', dest='list', action='store_true', help='list configuration variables')
  parser_config.add_argument('--edit', dest='edit', action='store_true', help='edit configuration directly')
  parser_config.add_argument('--testauth', dest='testauth', action='store_true', help='test authentication credentials')
  parser_config.add_argument('name', type=str, help='option name', nargs='?')
  parser_config.add_argument('value', type=str, help='option value', nargs='?')

  parser_update = subparsers.add_parser('update', help='check for updates')

  parser_version = subparsers.add_parser('version', help='show version')

  parser_balance = subparsers.add_parser('balance', help='show balance')

  parser_task = subparsers.add_parser('task', help='modify tasks')
  # parser_config.add_argument('--list', dest='task_list', action='store_true', help='list current tasks')
  parser_task.add_argument('name', type=str, help='task name', nargs='?')

  parser_order = subparsers.add_parser('order', help='order')
  parser_order.add_argument('pair', type=str, default="GHS/BTC", nargs='?', help="pair (default: GHS/BTC)")
  parser_order.add_argument('type', type=str, help='buy or sell (default: buy)', default="buy")
  parser_order.add_argument('price', type=str, default='market', help='price (default: market)', nargs='?')
  parser_order.add_argument('amount', type=str, help='amount')


  return parser.parse_args()
# coding: utf-8
import argparse
import sys


from albumthief import thief


class CLIDelegate(thief.ThiefDelegate):
	"""
	A Delegate that implements a CLI
	by conforming to ThiefDelegate protocol.
	"""

	def album_analysed(self, info):
		album_label = self.make_label('album')
		self._print("%s: %s" % (album_label, info['album_name']))
		num_image_label = self.make_label("number of images")
		self.num_images = info['num_images']
		self._print("%s: %s" % (num_image_label, self.num_images))

	def one_image_downloaded(self, info):
		progress_label = self.make_label("downloaded")
		self.inline_print("%s: %s/%s" % (
			progress_label,
			info['downloaded_image_count'],
			self.num_images
		))
		if info['downloaded_image_count'] == self.num_images:
			self._print("\nCompleted!")

	def make_label(self, name):
		name = name.title()
		label = name.ljust(20, ' ')
		return label

	def _print(self, line):
		print(line)

	def inline_print(self, line):
		sys.stdout.write('\r%s' % line)
		sys.stdout.flush()

def steal(album_id, concurrency, path):
	cli_delegate = CLIDelegate()
	t = thief.DouBanThief(album_id, cli_delegate)
	t.steal(concurrency, path)

def main():
	parser = argparse.ArgumentParser(prog='steal-album')
	parser.add_argument('album', type=int,
						help='The Album ID'
						)
	parser.add_argument('--concurrency',
						default=50,
						type=int, help='Downloading concurrency')
	parser.add_argument('--path',
						default='',
						type=str, help='Downloading directory')
	args = parser.parse_args()
	steal(args.album, args.concurrency, args.path)
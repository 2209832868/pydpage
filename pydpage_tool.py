#!/usr/bin/python3.7 
# -*- coding: utf-8 -*-  

'''
	titie: PYD文件打包助手
	description: 选择两个文件夹路径 
		将文件夹内所有的py脚本打包成pyd 更好的保护你的文件
	author: SDM
	create_datetime: 2020年12月28日12:13:00
	last_update_datetime: -
''' 

import tkinter as tk
from tkinter import ttk #tk的部件进阶
from tkinter import scrolledtext #滚动条文本
from tkinter import Menu #菜单栏
from tkinter import messagebox as msg #消息弹框
from tkinter import Tk #
from tkinter import Spinbox #数字调整框
from tkinter import filedialog as fd  #文件夹对话框

import os,sys,shutil,math,base64
from icon import Icon
from threading import Thread 	# 线程操作

from distutils.core import setup
from Cython.Build import cythonize

class PydPage():

	# 初始化函数
	def __init__(self):

		self.dirpath = ''		# 文件夹路径
		self.savepath = '' 		# 转换后的文件保存路径

		self.showinfo = False 	# 是否打开信息显示窗口
		
		# 获得当前文件绝对路径
		# 使用os.getcwd() 创建快捷方式时 位置会发生变动
		# self.curworkpath = os.getcwd()
		self.curworkpath = os.path.dirname(os.path.abspath(sys.argv[0]))

		self.win = Tk()
		self.win.title('pyd打包助手')
		self.win.resizable(False, False)

		with open('tmp.ico','wb') as tmp:
			tmp.write(base64.b64decode(Icon().img))
		self.win.iconbitmap('tmp.ico')
		os.remove('tmp.ico')

		self.win.attributes('-topmost', True)

		# 偏移坐标值
		self.xpos = self.win.winfo_x()	# 软件距离窗口X坐标
		self.ypos = self.win.winfo_y()	# 软件距离窗口Y坐标
		self.winwidth = self.win.winfo_reqwidth()	# 当前软件宽
		self.winheight = self.win.winfo_reqheight()	# 当前软件高
		# 绑定窗口移动事件 每次移动更新偏移坐标值
		self.win.bind('<Configure>', self._movewindow)
		
		# 页面初始化
		self.create_widget()

		# 创建信息显示面板
		self.create_infoplan()
		
	# 页面按钮
	def create_widget(self):
		self.main_frame = tk.Frame(self.win)
		self.main_frame.grid(padx=15, pady=15)

		# row 0
		ttk.Label(self.main_frame, text='py转换pyd文件'
			).grid(row=0,column=0)

		# row 1
		ttk.Label(self.main_frame, text='待转换文件夹'
			).grid(row=1,column=0)
		ttk.Button(self.main_frame, text='选择文件夹',
			command=self.covpathname).grid(row=1, column=1)
		self.showdirpath = ttk.Label(self.main_frame, text='对应路径')
		self.showdirpath.grid(row=1,column=2)

		# row 2
		ttk.Label(self.main_frame, text='保存到文件夹'
			).grid(row=2,column=0)
		ttk.Button(self.main_frame, text='选择文件夹',
			command=self.savepathname).grid(row=2, column=1)
		self.showsavepath = ttk.Label(self.main_frame, text='对应路径')
		self.showsavepath.grid(row=2,column=2)

		# row 3
		ttk.Button(self.main_frame, text='开始转换', width=25,
			command=self.covpdtopyd_btn
			).grid(row=3, column=0, columnspan=2, sticky='WE')
		self.infoplan = ttk.Button(self.main_frame, text='关闭信息 <<', 
			command=lambda:self.infoshow(self.showinfo))
		self.infoplan.grid(row=3, column=2)


		# padx, pady
		for child in self.main_frame.winfo_children():
			child.grid_configure(padx=5, pady=2, sticky='W')

	# 创建信息显示面板
	def create_infoplan(self):

		# 弹出窗口
		self.infowindow = tk.Toplevel()					# 建立顶级窗口
		#self.infowindow.withdraw()						# 隐藏窗口
		self.infowindow.attributes("-topmost", 1) 		# 窗口置顶
		self.infowindow.title('编译进度信息查看') 		# 窗口标题
		self.infowindow.attributes('-toolwindow', True)	# 自定义页面
		self.infowindow.protocol("WM_DELETE_WINDOW", 
			lambda:self.infoshow(self.showinfo)) 		# 重写关闭函数

		#row 0
		#滚动条
		text_y = tk.Scrollbar(self.infowindow)
		text_y.grid(row=0, column=1, sticky='NS')
		
		self.infotext = tk.Text(self.infowindow, 
			yscrollcommand = text_y.set)
		self.infotext.grid(row=0, column=0)
		text_y.config(command = self.infotext.yview) 	# 绑定滚动条操作

	# 文本改变事件
	def seeover(self):
		self.infotext.see(tk.END)
		self.infotext.update()

	# 更新偏移坐标值
	def _movewindow(self, event):
		self.xpos = self.win.winfo_x()
		self.ypos = self.win.winfo_y()

		self.winwidth = self.win.winfo_reqwidth()	# 当前软件宽
		self.winheight = self.win.winfo_reqheight()	# 当前软件高

		# 定义窗口位置
		self.infowindow.geometry("+{}+{}".format(self.xpos+self.winwidth, 
				self.ypos-4))

	# 转换文件夹路径选择
	def covpathname(self):
		fDir = ''
		self.dirpath = fd.askdirectory(parent=self.win, initialdir=fDir)
		self.showdirpath.configure(text=self.dirpath)

	# 保存文件夹路径选择
	def savepathname(self):
		fDir = ''
		self.savepath = fd.askdirectory(parent=self.win, initialdir=fDir)
		self.showsavepath.configure(text=self.savepath)

	# 显示信息面板
	def infoshow(self, showswitch):
		if showswitch:
			# 查看信息
			self.showinfo = False
			self.infoplan.configure(text='关闭信息 <<')
			self.infowindow.deiconify()
		else:
			# 关闭信息
			self.showinfo = True
			self.infoplan.configure(text='查看信息 >>')
			self.infowindow.withdraw()

	def covpdtopyd_btn(self):
		Thread(target=self.covpdtopyd).start()

	# 转换功能
	def covpdtopyd(self):

		if not all([self.dirpath, self.savepath]):
			self.infotext.insert(tk.END, '没有选择导入/保存路径\n')
			self.seeover()
			return

		wait_convert_list = []	# 等待编译的数组 # hello_covtext.py
		all_files = [] 			# 文件夹下的所有文件 含后缀
		nosuffix_files = []  	# 文件夹下的所有文件 不含后缀

		# 遍历对应文件夹下的所有文件
		for root, dirs, files in os.walk(self.dirpath, topdown=False):
			#print(root)		# 当前目录路径
			#print(dirs)		# 当前目录下所有子目录
			#print(files) 	# 当前路径下所有非目录子文件

			all_files = files

		# 去除后缀后进行保存
		nosuffix_files = [os.path.splitext(log)[0] for log in all_files]

		self.infotext.insert(tk.END, '======================\n')
		self.infotext.insert(tk.END, '开始生成编译文件\n')
		self.seeover()

		# 将文件逐一编译为pyd文件
		# 生成路径前 添加当前文件夹路径 避免运行时找不到对应文件
		for file_name in all_files:

			# 生成文件
			text_content = """#!/usr/bin/python3.7 
# -*- coding: gbk -*-  
# cython: language_level=3
print(r'{}')
import sys, os
sys.path.insert(0, r'{}')
print(sys.path)
from distutils.core import setup
from Cython.Build import cythonize

setup(
	name = '{}_cavpyd',
	ext_modules = cythonize("{}"))
			""".format(self.curworkpath, self.curworkpath,
				os.path.splitext(file_name)[0], file_name)

			covfilename = os.path.splitext(file_name)[0]
			covfilepath = self.dirpath + '/' + covfilename + '_covtext.py'
			wait_convert_name = covfilename + '_covtext.py'

			wait_convert_list.append(wait_convert_name)
			
			with open (covfilepath, 'w+') as f:
				f.write(text_content)

		# 执行编译
		text="""======================
执行编译 编译文件为
{}
=====================
请等待编译自动开始......
=====================
""".format(wait_convert_list)
		self.infotext.insert(tk.END, text)
		self.seeover()
	
		for convert in wait_convert_list:
			output_str = os.popen('{}: && cd {} && python {} build_ext --inplace'
				.format(self.dirpath[0], self.dirpath, convert))

			self.infotext.insert(tk.END, output_str.read())
			self.infotext.insert(tk.END,'======================\n')
			self.seeover()

		try:
			# 移除所有的编译文件 C文件 和 BUILD文件夹
			self.infotext.insert(tk.END,'移除文件\n======================\n')
			self.seeover()

			# 移除编译文件
			for convert in wait_convert_list:
				self.infotext.insert(tk.END,'开始移除' + self.dirpath + '/' 
					+ convert + '\n')
				self.infotext.insert(tk.END,'======================\n')
				self.seeover()
				os.remove(self.dirpath + '/' + convert)

			# 移除.C文件
			for newfilename in nosuffix_files:
				remove_file = newfilename + '.c'
				self.infotext.insert(tk.END,'开始移除' + self.dirpath + '/' 
					+ remove_file + '\n')
				self.infotext.insert(tk.END,'======================\n')
				self.seeover()
				os.remove(self.dirpath + '/' + remove_file)

			# 移除文件夹
			self.infotext.insert(tk.END, '开始移除' + self.dirpath + '/' 
				+ 'build' + '\n')
			self.infotext.insert(tk.END, '======================\n')
			self.seeover()
			shutil.rmtree(self.dirpath + '/' + 'build')

		except Exception as err:
			self.infotext.insert(tk.END, '因程序错误,相应文件未生成 无法移除\n \
				错误为:' + err + '\n')
			self.infotext.insert(tk.END, '======================\n')

		# pyd文件重命名并移动到保存的文件夹中
		for newfilename in nosuffix_files:
			forname = self.dirpath +'/'+ newfilename + '.cp37-win_amd64.pyd'
			toname = self.savepath +'/'+ newfilename + '.pyd'
			
			self.infotext.insert(tk.END, '重命名文件' + forname + ' 到 ' 
				+ toname + '\n')
			self.seeover()
			os.rename(forname, toname)

		self.infotext.insert(tk.END, '======================\n')
		self.infotext.insert(tk.END, '编译成功 请退出程序\n')
		self.seeover()

if __name__ == '__main__':
	pydpage = PydPage()
	pydpage.win.mainloop()


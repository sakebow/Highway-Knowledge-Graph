# -*- coding: utf-8 -*-

import pandas as pd
import itertools
import os

from py2neo import Node, Graph, Relationship, NodeMatcher

# 配置类
class CONFIG(enumerate):
  # Neo4j访问地址
  URL = 'http://localhost:1174'
  # 用户名
  USERNAME = 'neo4j'
  # 密码
  PASSWORD = 'ljx62149079'
  # xls文件路径
  XLS = os.getcwd() + '/knowledge/data.xls'
  # csv文件路径
  CSV = os.getcwd() + '/knowledge/data.csv'
  pass

# 数据导入类
class DataImporter:
  # 类构造器
  def __init__(self):
    # 直接从Excel里面读取所有的原生数据
    # self.raw_data = pd.read_excel(CONFIG.XLS)
    self.raw_data = pd.read_csv(CONFIG.CSV)
    # 将所有的数据提取到一维数组中（去重），没用...
    self.all_data = list(
      # 使用集合去重
      set([
        # 将一维数组字符串化
        str(i) for i in list(
          # 将二维数组展开成一维数组
          itertools.chain(*
            # 根据不同的属性获得所有的数据组成二维数组
            [item for item in self.raw_data[[
              # 获得所有的属性
              column for column in self.raw_data.columns
            ]].values]
          )
        )]
      )
    )
    # 所有的购买方（去重）
    self.buyer_list = list(set(self.raw_data['购买方名称']))
    # 所有的销售方（去重）
    self.seller_list = list(set(self.raw_data['销售方名称']))
    # 所有原生数据的映射
    self.dict = pd.DataFrame({
      # 所有的金额（原生）
      'finance': list(self.raw_data['金额']),
      # 所有的购买方（原生）
      'buyer': list(self.raw_data['购买方名称']),
      # 所有的销售方（原生）
      'seller': list(self.raw_data['销售方名称'])
    })
    # 图数据库对象
    self.graph = Graph(
      CONFIG.URL,
      username=CONFIG.USERNAME,
      password=CONFIG.PASSWORD
    )
    # 清空缓存
    self.graph.delete_all()
    # 配对器
    self.matcher = NodeMatcher(self.graph)
    pass

  # 创建节点方法
  def create_tree_node(self, buyers, sellers):
    for key in buyers: # 根据购买方创建节点
      self.graph.create(
        Node('buyer', name=key)
      )
      pass
    for key in sellers: # 根据销售方创建节点
      self.graph.create(
        Node('seller', name=key)
      )
      pass
    pass
  # 创建节点间关系
  def create_nodes_relation(self):
    # 对于字典中所有的数据
    for item in range(0, len(self.dict)):
      try:
        self.graph.create(
          Relationship(self.matcher.match('buyer').where("_.name='" + self.dict['buyer'][item] + "'").first(), self.dict['finance'][item], self.matcher.match('seller').where("_.name='" + self.dict['seller'][item] + "'").first())
        )
        pass
      # 如果出错，显示错误，增强程序健壮性
      except AttributeError as ae:
        print(ae, item)
        pass
      pass
    pass

  pass

if __name__ == '__main__':
  # 数据导入类
  dataImpoter = DataImporter()
  # 创建实体节点
  dataImpoter.create_tree_node(dataImpoter.buyer_list, dataImpoter.seller_list)
  # 创建实体节点间的关系
  dataImpoter.create_nodes_relation()
  pass
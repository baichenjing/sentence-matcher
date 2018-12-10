# sentence-matcher 0.2.0
根据语法规则匹配句子
> 语法规则及交互树详见 [interactive-syntax-tree](https://wzyjerry.github.io/interactive-syntax-tree/)
---
## 输入
语法树，通过-f参数传入，格式如下:
``` json
{
    "type": "root",
    "children": [{
        "type":"intent",
        "weight":1,
        "intent":"intent 1",
        ...
    },
    ...]
}
```
待匹配的句子，已进行过NER，通过-q参数传入，格式如下：
``` json
{
  "query": "which are ORG1 DATE1 PER1 's CON2 papers related to KEY2 from done at DATE1 published on CON2",
  "entities": {
    "5bfe132cc4952f342f394a48": ["KEY2"],
    "5bfe137dc4952f342f394a49": ["ORG1"],
    "5bfe0ef9c4952f342f394a44": ["DATE1"],
    "5bfe111cc4952f342f394a45": ["CON2"],
    "5bfe127cc4952f342f394a47": ["PER1"]
  }
}
```
---
## 输出
匹配的意图
---
## 算法步骤
1. 编译语法树
2. 由绿色节点content、NER结果构造AC自动机
3. 由节点dropout规则生成节点nullable属性
4. 对query进行匹配，得到绿色节点的匹配区间
5. 在树上根据规则进行线段合并

## 示例
python main.py -f data/rule.json -q data/demo1.json
输出：搜文章

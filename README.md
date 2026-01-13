# McPunction(McPn)

파이썬으로 데이터팩 작성할 수 있게 해주는 프로젝트입니다.

## 설치

프로젝트 최상단에서:
```sh
pip install -e .
```

## Hello, World!
```py
import mcpunction as pn

class HelloWorld(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
        @pn.onload
        def main(self):
                pn.raw("say Hello, World!")
new_dtpk=HelloWorld()
pn.make(new_dtpk,"./hello_dtpk")
```

## 데이터팩 생성

`Dtpk`을 상속받는 클래스를 정의하여 데이터팩을 생성하실 수 있습니다.


`Dtpk`을 상속받아 정의된 클래스는 이제부터 `데이터팩 클래스`라고 부르겠습니다.


__init__으로 version과 namespace를 설정해주셔야 합니다.


실제 데이터팩 파일을 생성하기 위해서는 `pn.make` 함수에 데이터팩 클래스 인스턴스와 출력 경로를 넘겨주시면 됩니다.

```py
import mcpunction as pn

class ExamplePack(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="example"

pn.make(ExamplePack(),"./example_dtpk")
```

## 함수

함수를 만들기 위해서는 데이터팩 클래스에 메서드를 추가하시면 됩니다.


함수는 `<namespace>:<함수이름>`에 저장됩니다.

```py
import mcpunction as pn

class ExamplePack(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="example"
        def hello(self):
                pn.raw("say hi")
pn.make(ExamplePack(),"./example_dtpk")
```

여러 데코레이터를 사용하여 함수 실행 조건이나, 함수의 용도를 변경할 수 있습니다.

```py
import mcpunction as pn

class ExamplePack(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="example"
        @pn.mac
        def hello(self,name): # 더 이상 데이터팩의 함수로 취급되지 않고, 파이썬의 함수로 취급됩니다. `.mcfunction` 함수를 생성하지 않습니다.
                pn.raw(f"say Hello, {name}!")
        @pn.onload
        def load(self): # 데이터팩 로드 시 실행됩니다.
                hello("load") # `say Hello, load!`를 load.mcfunction에 작성합니다.
        @pn.ontick
        def tick(self): # 매 틱마다 실행됩니다.
                hello("tick") # `say Hello, tick!`을 tick.mcfunction에 작성합니다.
pn.make(ExamplePack(),"./example_dtpk")
```

## 명령

마인크래프트의 명령을 사용하기 위해서는 `raw()` 함수를 사용합니다.


`raw()`에 넘긴 문자열이 그대로 `.mcfunction`에 작성됩니다.

```py
class ExamplePack(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="example"
        def func(self):
                pn.raw("tp ~ ~1 ~") # `func.mcfunction`에 `tp ~ ~1 ~`이 작성됩니다
pn.make(ExamplePack(),"./example_dtpk")
```

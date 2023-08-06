import PyV8

class JSWalker(object):

    def __init__(self):
        self._positions = []

    def __call__(self, src):
        self.run(src)
        return self._positions

    def __enter__(self):
        self.ctxt = PyV8.JSContext()
        self.ctxt.enter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ctxt.leave()

    def add_position(self, pos, node=None):
        if pos > -1:
            self._positions.append(pos)

    def run(self, script):
        PyV8.JSEngine().compile(script).visit(self)

    def onProgram(self, prog):
        prog.visit(self)

    # Declarations

    def onVariableDeclaration(self, node):
        pass

    def onFunctionDeclaration(self, node):
        node.function.visit(self)

    def onModuleDeclaration(self, node):
        raise NotImplementedError()

    def onImportDeclaration(self, node):
        raise NotImplementedError()

    def onExportDeclaration(self, node):
        raise NotImplementedError()

    # Modules

    def onModuleLiteral(self, node):
        raise NotImplementedError()

    def onModuleVariable(self, node):
        raise NotImplementedError()

    def onModulePath(self, node):
        raise NotImplementedError()

    def onModuleUrl(self, node):
        raise NotImplementedError()

    # Statements

    def onBlock(self, node):
        #print 'block',node.pos,js[node.pos:node.pos+10]
        self.add_position(node.pos)
        for stmt in node.statements:
            stmt.visit(self)

    def onModuleStatement(self, node):
        raise NotImplementedError()

    def onExpressionStatement(self, node):
        self.add_position(node.pos)
        node.expression.visit(self)

    def onEmptyStatement(self, node):
        raise NotImplementedError()

    def onIfStatement(self, node):
        self.add_position(node.pos)
        node.thenStatement.visit(self)

    def onContinueStatement(self, node):
        raise NotImplementedError()

    def onBreakStatement(self, node):
        raise NotImplementedError()

    def onReturnStatement(self, node):
        self.add_position(node.pos)

    def onWithStatement(self, node):
        raise NotImplementedError()

    def onSwitchStatement(self, node):
        self.add_position(node.pos, node)
        for case in node.cases:
            case.visit(self)

    def onDoWhileStatement(self, node):
        raise NotImplementedError()

    def onWhileStatement(self, node):
        self.add_position(node.pos, node)
        node.body.visit(self)

    def onForStatement(self, node):
        self.add_position(node.pos, node)
        node.body.visit(self)
        #raise NotImplementedError()

    def onForInStatement(self, node):
        raise NotImplementedError()

    def onForOfStatement(self, node):
        raise NotImplementedError()

    def onTryCatchStatement(self, node):
        raise NotImplementedError()

    def onTryFinallyStatement(self, node):
        raise NotImplementedError()

    def onDebuggerStatement(self, node):
        raise NotImplementedError()

    # Expressions

    def onFunctionLiteral(self, func):
        #print func.toAST()
        for decl in func.scope.declarations:
            decl.visit(self)
        for stmt in func.body:
            stmt.visit(self)

    def onNativeFunctionLiteral(self, node):
        raise NotImplementedError()

    def onConditional(self, node):
        raise NotImplementedError()

    def onVariableProxy(self, node):
        pass

    def onLiteral(self, node):
        pass

    def onRegExpLiteral(self, node):
        raise NotImplementedError()

    def onObjectLiteral(self, node):
        # TODO: Bug in PyV8 prevents accessing node.properties.
        pass

    def onArrayLiteral(self, node):
        for val in node.values:
            val.visit(self)

    def onAssignment(self, node):
        node.value.visit(self)

    def onYield(self, node):
        raise NotImplementedError()

    def onThrow(self, node):
        raise NotImplementedError()

    def onProperty(self, node):
        pass

    def onCall(self, node):
        node.expression.visit(self)

    def onCallNew(self, node):
        node.expression.visit(self)

    def onCallRuntime(self, node):
        #print node
        return
        if node.name != 'InitializeVarGlobal':
            raise NotImplementedError()
        raise NotImplementedError()
        self.positions.append(node.pos)

    def onUnaryOperation(self, node):
        raise NotImplementedError()

    def onCountOperation(self, node):
        raise NotImplementedError()

    def onBinaryOperation(self, node):
        pass

    def onCompareOperation(self, node):
        raise NotImplementedError()

    def onThisFunction(self, node):
        raise NotImplementedError()

    def onCaseClause(self, node):
        #print node.statements
        #print dir(node)
        raise NotImplementedError()

def instrument(js):
    out = []
    with JSWalker() as walker:
        positions = walker(js)
        positions.sort()
        prev = 0
        for pos in positions:
            out.append(js[prev:pos])
            out.append('track({});'.format(pos))
            prev = pos
        out.append(js[pos:])
    return ''.join(out)

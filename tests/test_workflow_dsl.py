from workflows.dsl import compile_dsl


def test_compile_simple_dsl_workflow():
    source = """
    workflow dsl_demo {
      node start plugin echo {
        message: "hello"
      }
      node clean plugin text.normalize {
        text: "  Hi  "
        lowercase: true
        strip: true
      } depends start
    }
    """
    workflow = compile_dsl(source)
    assert workflow.name == "dsl_demo"
    assert len(workflow.nodes) == 2
    assert workflow.nodes[1].depends_on == ["start"]


def test_dsl_supports_numeric_input():
    source = """
    workflow numbers {
      node add plugin add_numbers {
        a: 2
        b: 3
      }
    }
    """
    workflow = compile_dsl(source)
    assert workflow.nodes[0].input["a"] == 2

"""TAP dcom plugin — the design / configuration / operation axis as a dimension pack.

Ships four `dimension` nodes (`dcom`, `dcom.design`, `dcom.configuration`,
`dcom.operation`) and nothing else. Other plugins inherit the axis by declaring
`dcom` in `depends_on` and stamping the label on the types they own.

Spec: specs/spec-dcom-v0.md.
"""

package silly

import "testing"

func TestNothing(t *testing.T) {
	const in, out = 1, 2
	if in != out {
		t.Errorf("%v is not %v", in, out)
	}
}

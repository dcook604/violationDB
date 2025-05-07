import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Logo from "../../components/common/Logo";
import Input from "../../components/common/Input";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth();

  const logoPath = "/logospectrum.png";
  const logoBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAABkCAYAAAA8AQ3AAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OEI5RDc5RDY3NjAxMTFFOUI0QTk4RjYwQUMzQUQwMEIiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6OEI5RDc5RDc3NjAxMTFFOUI0QTk4RjYwQUMzQUQwMEIiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo4QjlENzlENDc2MDExMUU5QjRBOThGNjBBQzNBRDAwQiIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo4QjlENzlENTc2MDExMUU5QjRBOThGNjBBQzNBRDAwQiIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PnRj7mUAAAWqSURBVHja7J1NbBVFFMd3oRRCi6XWmgDSQiXxg9iqiTGRhYkhwYUkLkzcGs0x0YUmaowmJroySjRuCCYmujFqTEjcIG5caAyfoiYqihgNUgvFQmuhlOdjTji2j/fee2/evHlz5v+TJqXtvM6d85/fnDNnZm7LwsKCcZxms+kOJz3aR8+rbY2eU0HLKVBC/bRN9PwhPe+eH/5fE/w4jtlmHTJmC1Kwwqh+jGbTdTH3SQpMMqfL+AvG26/CQPvpnEpqT6etK1UhZ/RsZ8qqgPbPdlNfxXWCTuVMVSG6PUdVYcpx36oCaFNWEZqE/UwC10/l1DH1pqByOJVT2VTC2/M6t3OPqDRDlNVRYbxu9xEfZv02GRxBOVFWPcmcQs4JKavxoG3ylmC/G5KoWCZf9kFZEX+UrfWZ9kRZbShZPyirTlnjhLJKeXlOuFhCMjAMK42sMHe0WVsLskrRJ4OjlNc9IRmYMJemjYj5JaUkZYUk7TFmdGVb56yj2GIuLVsb3cQmI3YeacvH5J9bWxtnNijAx1JpBnLQbxQgfxmXtp4ktFvfVQXnAEEZbSE1H8aJVbXEhh0m9YWdCpKB7Kb0j57vSSirhikrGH/+NRhDwkXnTNxgIqx+YX5yzuDshAx2BXWjNiGdbMPCGFDFWIeJMY38jQZl6WSVovWrxUxNHvh16xyULHRuLCclJwPz/E1jVrAYm8fZRlRp7Wlgr1NKXjd53IblaU4lH/QpzMZnKGX1xI+k16/OGe05LlPLbZSe92VqeYmvzhkVJgP1UzCfYlNWEcmAyqsavOxOAh0NlcK5I+XN0CcsnTP97SXNbEwu0Nj7qcl3u0n97Cj3CUBZgUxZpA3CSplqtX0QVpyzYdOxWTBuPmiFglB5u/AeLeaOJpk7Gma7GiTh2VFUfepXlXPvV2f6LNnDsj41sGD/ijYZ+A4FazXZpxTWo67n4Nz39H+Fj2dZM5I8wzIlZ1QrCWeVFGzwVnZzSRCsWemcUQ6FScKzI+e+8rBo3xphJd1VjnTDr+HhQoFOqcKrTPpnJ2tLXTuPO5QgJpXVkUXxCbdF+ic0TnsZu5ozLQtK6v19yAsnQz2JNwvvGdkMsDWBW1SHR4WqhhZoXPG2SgglX5Zk0q0H2Bzpmzc36GBcyMqsZ7ZdXrZ1jgbHBW0zFe/P5a8YPRHsIG0D7RjMrJnGqBLlEw8Y63a2wqhJVnzqjEvbIaYE610bmjs6a5zrCZVuW0l+RuDTJ35N2P3vewgLaO1uicgc4ZpSUL546Q87xmWBVGZuZYc0eQgb+UJAMlKCuQYt6nrKUU9snV1Jz7KsiqXmxMYa0hh1Pxc+5Bz7mdYSEZGLfOIZdTaTI4rtfYkJuz+i0IitZFE78Hp9fJgOqJFD8ntBxZLZUMLJjyJINF+21kMlCHsLz+MU5qVeqcqXM/fLfYDKvI3JGvOdXKJs+2GvgFIIuCUU60VaHYvZBZJr3LyB213Q93LvVLp1lYCo4/V1bJY6ltbW2VOrfP+GVBvJ2NXaGsUg49VeFxBGV1xKTbC1jU8FMm/xZT9NxR17nDwNPG81lYg0YFUS8VxmtVvE+nraJ2YLwB2BxcEAj2sKp2nrhKBkrcX0c8C9ZphBWtvIYCWa0YSjRYLKcS4mVa58pqxVmXjWGFZTXI2F/KZGCS7RFuoqw5kDFHIwPOCB9lGUm5XVIGsuA9rLxwLbAiE1oKMlhvp7rXk4ElZA+rSDKQdeQtU1aFzmVd6z1hMrACtGm/YYtJBtSu/xQ1h1g6GWgy3sMq6OQq2GVJQGfZBpVREXWTgdzDSjh0Vrif50KyVFnNuJYMyHiPnAxkDyvO0CuVlTqXUjdldTrgpaxMCckAHBcQFgCEBQAQLPj/Afa0YeJ+kS7RAAAAAElFTkSuQmCC";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Email and password are required");
      return;
    }
    try {
      await login({ email, password }, rememberMe);
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Login failed. Please check your credentials.");
      }
    }
  };

  return (
    <div className="container mx-auto px-4 h-full">
      <div className="flex content-center items-center justify-center h-full">
        <div className="w-full lg:w-4/12 px-4">
          <div className="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-lg bg-white border-0">
            <div className="rounded-t mb-0 px-6 py-6">
              <Logo src={logoPath} alt="Spectrum 4 Logo" base64Fallback={logoBase64} />
              <div className="text-center mb-3">
                <h6 className="text-blueGray-500 text-sm font-bold">
                  Sign in with credentials
                </h6>
              </div>
              <hr className="mt-6 border-b-1 border-blueGray-300" />
            </div>
            <div className="flex-auto px-4 lg:px-10 py-10 pt-0">
              <form onSubmit={handleSubmit}>
                <Input
                  id="email"
                  type="email"
                  label="Email"
                  placeholder="Email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
                <Input
                  id="password"
                  type="password"
                  label="Password"
                  placeholder="Password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-lightBlue-500 focus:ring-lightBlue-400 border-gray-300 rounded"
                      checked={rememberMe}
                      onChange={e => setRememberMe(e.target.checked)}
                    />
                    <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                      Remember me
                    </label>
                  </div>
                  <div>
                    <Link
                      to="/forgot-password"
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Forgot password?
                    </Link>
                  </div>
                </div>
                <div className="text-center mt-6">
                  <button
                    className="bg-lightBlue-500 text-white active:bg-lightBlue-600 text-sm font-bold uppercase px-6 py-3 rounded shadow hover:shadow-lg outline-none focus:outline-none mr-1 mb-1 w-full ease-linear transition-all duration-150"
                    type="submit"
                  >
                    Sign In
                  </button>
                </div>
                {error && (
                  <div className="text-red-500 text-center text-sm font-semibold mt-4">
                    {error}
                  </div>
                )}
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
"""
Implements convolutional networks in PyTorch.
WARNING: you SHOULD NOT use ".to()" or ".cuda()" in each implementation block.
"""
import torch
from fully_connected_networks import Linear_ReLU, Linear, Solver, adam, ReLU, softmax_loss


def hello_convolutional_networks():
    """
    This is a sample function that we will try to import and run to ensure that
    our environment is correctly set up on Google Colab.
    """
    print('Hello from convolutional_networks.py!')


class Conv(object):

    @staticmethod
    def forward(x, w, b, conv_param):
        """
        A naive implementation of the forward pass for a convolutional layer.
        The input consists of N data points, each with C channels, height H and
        width W. We convolve each input with F different filters, where each
        filter spans all C channels and has height HH and width WW.

        Input:
        - x: Input data of shape (N, C, H, W)
        - w: Filter weights of shape (F, C, HH, WW)
        - b: Biases, of shape (F,)
        - conv_param: A dictionary with the following keys:
          - 'stride': The number of pixels between adjacent receptive fields
            in the horizontal and vertical directions.
          - 'pad': The number of pixels that is used to zero-pad the input.

        During padding, 'pad' zeros should be placed symmetrically (i.e equally
        on both sides) along the height and width axes of the input. Be careful
        not to modfiy the original input x directly.

        Returns a tuple of:
        - out: Output data of shape (N, F, H', W') where H' and W' are given by
          H' = 1 + (H + 2 * pad - HH) / stride
          W' = 1 + (W + 2 * pad - WW) / stride
        - cache: (x, w, b, conv_param)
        """
        out = None
        N, C, H, W = x.shape
        F, C1, HH, WW = w.shape
        st = conv_param['stride']
        pd =  conv_param['pad']
        xpadding = torch.nn.functional.pad(x, (pd, pd, pd, pd),"constant", 0) 
        Hout = 1 + (H + 2 * pd - HH) // st
        Wout = 1 + (W + 2 * pd - WW) // st
        out = torch.zeros((N, F, Hout, Wout),dtype=torch.float64, device=x.device)
        for num in range(N):
          for k in range(F):
            for i in range(0, Hout):
                for j in range(0, Wout):
                    verticalstart = i * st
                    verticalend = verticalstart + HH
                    horizontalstart = j * st
                    horizontalend = horizontalstart + WW
                    slicing = xpadding[num, :, verticalstart:verticalend, horizontalstart:horizontalend]
                    out[num, k, i, j] = torch.sum(slicing * w[k]) + b[k]
        cache = (x, w, b, conv_param)
        cache = (x, w, b, conv_param)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        A naive implementation of the backward pass for a convolutional layer.
          Inputs:
        - dout: Upstream derivatives.
        - cache: A tuple of (x, w, b, conv_param) as in conv_forward_naive

        Returns a tuple of:
        - dx: Gradient with respect to x
        - dw: Gradient with respect to w
        - db: Gradient with respect to b
        """
        dx, dw, db = None, None, None
        x, w, b, conv_param = cache
        N, C, H, W = x.shape
        F, C2, HH, WW = w.shape
        st = conv_param['stride']
        pd = conv_param['pad']
        Hout = 1 + (H + 2*pd - HH) // st
        Wout = 1 + (W + 2*pd - WW) // st
        xpadding = torch.nn.functional.pad(x, (pd, pd, pd, pd), 'constant', 0)
        dx = torch.zeros_like(x)
        dpad = torch.zeros_like(xpadding)
        dw = torch.zeros_like(w)
        db = torch.zeros_like(b)
        for num in range(N):
          for k in range(F):
            db[k] += torch.sum(dout[num, k])
            for i in range(0, Hout):
              for j in range(0, Wout):
                verticalstart = i * st
                verticalend = verticalstart + HH
                horizontalstart = j * st 
                horizontalend = horizontalstart + WW
                dw[k] += xpadding[num, :, verticalstart:verticalend, horizontalstart:horizontalend] * dout[num, k, i, j]
                dpad[num, :, verticalstart:verticalend, horizontalstart:horizontalend] += w[k] * dout[num, k, i, j]
        dx = dpad[:,:,pd:-pd,pd:-pd]  
        return dx, dw, db


class MaxPool(object):

    @staticmethod
    def forward(x, pool_param):
        """
        A naive implementation of the forward pass for a max-pooling layer.

        Inputs:
        - x: Input data, of shape (N, C, H, W)
        - pool_param: dictionary with the following keys:
          - 'pool_height': The height of each pooling region
          - 'pool_width': The width of each pooling region
          - 'stride': The distance between adjacent pooling regions
        No padding is necessary here.

        Returns a tuple of:
        - out: Output of shape (N, C, H', W') where H' and W' are given by
          H' = 1 + (H - pool_height) / stride
          W' = 1 + (W - pool_width) / stride
        - cache: (x, pool_param)
        """
        out = None
        N,C,H,W = x.shape
        pheight = pool_param['pool_height']
        pwidth = pool_param['pool_width']
        st = pool_param['stride']
        Heightp = 1 + (H - pheight) // st
        Weightp = 1 + (W - pwidth) // st
        out = torch.zeros((N,C,Heightp,Weightp),dtype=torch.float64, device=x.device)
        for num in range(N):
          for chan in range(C):
            for hei in range(Heightp):
                for wei in range(Weightp):
                    heightstart = hei * st
                    heightend = heightstart + pheight
                    weightstart = wei * st
                    weightend = weightstart + pwidth
                    x_pool = x[num, chan, heightstart:heightend, weightstart:weightend]
                    out[num, chan, hei, wei] = torch.max(x_pool)
        cache = (x, pool_param)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        A naive implementation of the backward pass for a max-pooling layer.
        Inputs:
        - dout: Upstream derivatives
        - cache: A tuple of (x, pool_param) as in the forward pass.
        Returns:
        - dx: Gradient with respect to x
        """
        dx = None
        x, pool_param = cache
        N, C, H, W = x.shape
        pheight = pool_param['pool_height']
        pwidth = pool_param['pool_width']
        st = pool_param['stride']
        Heightp = 1 + (H - pheight) // st
        Weightp = 1 + (W - pwidth) // st
        dx = torch.zeros_like(x, dtype=torch.float64, device=x.device)
        for num in range(N):
          for chan in range(C):
            for hei in range(Heightp):
                for wei in range(Weightp):
                    heightstart = hei * st
                    heightend = heightstart + pheight
                    weightstart = wei * st
                    weightend = weightstart + pwidth
                    x_pool = x[num, chan, heightstart:heightend, weightstart:weightend]
                    mask = (x_pool == torch.max(x_pool))
                    dx[num, chan, heightstart:heightend, weightstart:weightend] += mask * dout[num, chan, hei, wei]

        return dx


class ThreeLayerConvNet(object):
    """
    A three-layer convolutional network with the following architecture:
    conv - relu - 2x2 max pool - linear - relu - linear - softmax
    The network operates on minibatches of data that have shape (N, C, H, W)
    consisting of N images, each with height H and width W and with C input
    channels.
    """

    def __init__(self,
                 input_dims=(3, 32, 32),
                 num_filters=32,
                 filter_size=7,
                 hidden_dim=100,
                 num_classes=10,
                 weight_scale=1e-3,
                 reg=0.0,
                 dtype=torch.float,
                 device='cpu'):
        """
        Initialize a new network.
        Inputs:
        - input_dims: Tuple (C, H, W) giving size of input data
        - num_filters: Number of filters to use in the convolutional layer
        - filter_size: Width/height of filters to use in convolutional layer
        - hidden_dim: Number of units to use in fully-connected hidden layer
        - num_classes: Number of scores to produce from the final linear layer.
        - weight_scale: Scalar giving standard deviation for random
          initialization of weights.
        - reg: Scalar giving L2 regularization strength
        - dtype: A torch data type object; all computations will be performed
          using this datatype. float is faster but less accurate, so you
          should use double for numeric gradient checking.
        - device: device to use for computation. 'cpu' or 'cuda'
        """
        self.params = {}
        self.reg = reg
        self.dtype = dtype
        self.params['W1'] = torch.randn(num_filters, input_dims[0], filter_size, filter_size, dtype=dtype, device=device) * weight_scale
        self.params['b1'] = torch.zeros(num_filters, dtype=dtype, device=device)
        pool_output_size = num_filters * (input_dims[1] // 2) * (input_dims[2] // 2)
        self.params['W2'] = torch.randn(pool_output_size, hidden_dim, dtype=dtype, device=device) * weight_scale
        self.params['b2'] = torch.zeros(hidden_dim, dtype=dtype, device=device)
        self.params['W3'] = torch.randn(hidden_dim, num_classes, dtype=dtype, device=device) * weight_scale
        self.params['b3'] = torch.zeros(num_classes, dtype=dtype, device=device)
    def save(self, path):
        checkpoint = {
          'reg': self.reg,
          'dtype': self.dtype,
          'params': self.params,
        }
        torch.save(checkpoint, path)
        print("Saved in {}".format(path))

    def load(self, path):
        checkpoint = torch.load(path, map_location='cpu')
        self.params = checkpoint['params']
        self.dtype = checkpoint['dtype']
        self.reg = checkpoint['reg']
        print("load checkpoint file: {}".format(path))

    def loss(self, X, y=None):
        """
        Evaluate loss and gradient for the three-layer convolutional network.
        Input / output: Same API as TwoLayerNet.
        """
        X = X.to(self.dtype)
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        W3, b3 = self.params['W3'], self.params['b3']
        filter_size = W1.shape[2]
        conv_param = {'stride': 1, 'pad': (filter_size - 1) // 2}
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

        scores = None
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        W3, b3 = self.params['W3'], self.params['b3']
        conv_param = {'stride': 1, 'pad': (W1.shape[2] - 1) // 2}
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}
        X = X.to(self.dtype)
        cout, ccache = Conv_ReLU_Pool.forward(X, W1, b1, conv_param, pool_param)
        aout, acache = Linear_ReLU.forward(cout, W2, b2)
        scores, scache = Linear.forward(aout, W3, b3)
        if y is None:
            return scores

        loss, grads = 0.0, {}
        loss, grads = 0.0, {}
        loss, dscores = softmax_loss(scores, y)
        loss += 0.5 * self.reg * (torch.sum(W1**2) + torch.sum(W2**2) + torch.sum(W3**2))
        hd, grads['W3'], grads['b3'] = Linear.backward(dscores, scache)
        dout, grads['W2'], grads['b2'] = Linear_ReLU.backward(hd, acache)
        dx, grads['W1'], grads['b1'] = Conv_ReLU_Pool.backward(dout, ccache)
        grads['W3'] += self.reg * W3
        grads['W2'] += self.reg * W2
        grads['W1'] += self.reg * W1
        return loss, grads


class DeepConvNet(object):
    """
    A convolutional neural network with an arbitrary number of convolutional
    layers in VGG-Net style. All convolution layers will use kernel size 3 and
    padding 1 to preserve the feature map size, and all pooling layers will be
    max pooling layers with 2x2 receptive fields and a stride of 2 to halve the
    size of the feature map.

    The network will have the following architecture:

    {conv - [batchnorm?] - relu - [pool?]} x (L - 1) - linear

    Each {...} structure is a "macro layer" consisting of a convolution layer,
    an optional batch normalization layer, a ReLU nonlinearity, and an optional
    pooling layer. After L-1 such macro layers, a single fully-connected layer
    is used to predict the class scores.

    The network operates on minibatches of data that have shape (N, C, H, W)
    consisting of N images, each with height H and width W and with C input
    channels.
    """
    def __init__(self,
                 input_dims=(3, 32, 32),
                 num_filters=[8, 8, 8, 8, 8],
                 max_pools=[0, 1, 2, 3, 4],
                 batchnorm=False,
                 num_classes=10,
                 weight_scale=1e-3,
                 reg=0.0,
                 weight_initializer=None,
                 dtype=torch.float,
                 device='cpu'):
        """
        Initialize a new network.

        Inputs:
        - input_dims: Tuple (C, H, W) giving size of input data
        - num_filters: List of length (L - 1) giving the number of
          convolutional filters to use in each macro layer.
        - max_pools: List of integers giving the indices of the macro
          layers that should have max pooling (zero-indexed).
        - batchnorm: Whether to include batch normalization in each macro layer
        - num_classes: Number of scores to produce from the final linear layer.
        - weight_scale: Scalar giving standard deviation for random
          initialization of weights, or the string "kaiming" to use Kaiming
          initialization instead
        - reg: Scalar giving L2 regularization strength. L2 regularization
          should only be applied to convolutional and fully-connected weight
          matrices; it should not be applied to biases or to batchnorm scale
          and shifts.
        - dtype: A torch data type object; all computations will be performed
          using this datatype. float is faster but less accurate, so you should
          use double for numeric gradient checking.
        - device: device to use for computation. 'cpu' or 'cuda'
        """
        self.params = {}
        self.num_layers = len(num_filters)+1
        self.max_pools = max_pools
        self.batchnorm = batchnorm
        self.reg = reg
        self.dtype = dtype

        if device == 'cuda':
            device = 'cuda:0'
        C, H, W = input_dims
        L = self.num_layers
        shrink = 4 ** len(set(max_pools)) 

        if isinstance(weight_scale, str):  
          for layer, F in enumerate(num_filters):
            self.params[f'W{layer+1}'] = kaiming_initializer(F,C,3,dtype=dtype,device=device)
            self.params[f'b{layer+1}'] = torch.zeros(F,dtype=dtype,device=device)
            
            if self.batchnorm:
              self.params[f'gamma{layer+1}'] = torch.ones(F,dtype=dtype,device=device)
              self.params[f'beta{layer+1}'] = torch.zeros(F,dtype=dtype,device=device)
            C = F  
            
          self.params[f'W{L}'] = kaiming_initializer(C*H*W//shrink,num_classes,dtype=dtype,device=device)
        
        else:
          for layer, F in enumerate(num_filters):
            self.params[f'W{layer+1}'] = weight_scale * torch.randn(F,C,3,3,dtype=dtype,device=device)
            self.params[f'b{layer+1}'] = torch.zeros(F,dtype=dtype,device=device)
            
            if self.batchnorm:
              self.params[f'gamma{layer+1}'] = torch.ones(F,dtype=dtype,device=device)
              self.params[f'beta{layer+1}'] = torch.zeros(F,dtype=dtype,device=device)
            C = F 

          self.params[f'W{L}'] = weight_scale * torch.randn(C*H*W//shrink,num_classes,dtype=dtype,device=device)
        
        self.params[f'b{L}'] = torch.zeros(num_classes,dtype=dtype,device=device) 
        self.bn_params = []
        if self.batchnorm:
            self.bn_params = [{'mode': 'train'}
                              for _ in range(len(num_filters))]

        # Check that we got the right number of parameters
        if not self.batchnorm:
            params_per_macro_layer = 2  # weight and bias
        else:
            params_per_macro_layer = 4  # weight, bias, scale, shift
        num_params = params_per_macro_layer * len(num_filters) + 2
        msg = 'self.params has the wrong number of ' \
              'elements. Got %d; expected %d'
        msg = msg % (len(self.params), num_params)
        assert len(self.params) == num_params, msg

        # Check that all parameters have the correct device and dtype:
        for k, param in self.params.items():
            msg = 'param "%s" has device %r; should be %r' \
                  % (k, param.device, device)
            assert param.device == torch.device(device), msg
            msg = 'param "%s" has dtype %r; should be %r' \
                  % (k, param.dtype, dtype)
            assert param.dtype == dtype, msg

    def save(self, path):
        checkpoint = {
          'reg': self.reg,
          'dtype': self.dtype,
          'params': self.params,
          'num_layers': self.num_layers,
          'max_pools': self.max_pools,
          'batchnorm': self.batchnorm,
          'bn_params': self.bn_params,
        }
        torch.save(checkpoint, path)
        print("Saved in {}".format(path))

    def load(self, path, dtype, device):
        checkpoint = torch.load(path, map_location='cpu')
        self.params = checkpoint['params']
        self.dtype = dtype
        self.reg = checkpoint['reg']
        self.num_layers = checkpoint['num_layers']
        self.max_pools = checkpoint['max_pools']
        self.batchnorm = checkpoint['batchnorm']
        self.bn_params = checkpoint['bn_params']

        for p in self.params:
            self.params[p] = \
                self.params[p].type(dtype).to(device)

        for i in range(len(self.bn_params)):
            for p in ["running_mean", "running_var"]:
                self.bn_params[i][p] = \
                    self.bn_params[i][p].type(dtype).to(device)

        print("load checkpoint file: {}".format(path))

    def loss(self, X, y=None):
        """
        Evaluate loss and gradient for the deep convolutional
        network.
        Input / output: Same API as ThreeLayerConvNet.
        """
        X = X.to(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params since they
        # behave differently during training and testing.
        if self.batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None

        # pass conv_param to the forward pass for the
        # convolutional layer
        # Padding and stride chosen to preserve the input
        # spatial size
        filter_size = 3
        conv_param = {'stride': 1, 'pad': (filter_size - 1) // 2}

        # pass pool_param to the forward pass for the max-pooling layer
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

        scores = None
        cache_dict, L = {}, self.num_layers
        max_pools = set(self.max_pools)
        out = X
        if self.batchnorm:
          for layer in range(1,L): 
            W, b = self.params[f'W{layer}'], self.params[f'b{layer}']
            gamma, beta = self.params[f'gamma{layer}'], self.params[f'beta{layer}']
            bn_param = self.bn_params[layer-1]        
            if layer - 1 in max_pools: out, cache_dict[layer] = Conv_BatchNorm_ReLU_Pool.forward(out,W,b,gamma,beta,conv_param,bn_param,pool_param)  
            else: out, cache_dict[layer] = Conv_BatchNorm_ReLU.forward(out,W,b,gamma,beta,conv_param,bn_param)
        else:
          for layer in range(1,L):
            W, b = self.params[f'W{layer}'], self.params[f'b{layer}']
            if layer - 1 in max_pools: out, cache_dict[layer] = Conv_ReLU_Pool.forward(out,W,b,conv_param,pool_param)
            else: out, cache_dict[layer] = Conv_ReLU.forward(out,W,b,conv_param)    
        out, cache_dict[L] = Linear.forward(out,self.params[f'W{L}'],self.params[f'b{L}'])
        scores = out
        if y is None:
            return scores
        loss, grads = 0, {}
        loss, dout = softmax_loss(scores, y)
        for i in range(1,L+1): loss += self.reg * (self.params[f'W{i}']**2).sum()
        
        dout, dw, db = Linear.backward(dout,cache_dict[L])
        grads[f'W{L}'], grads[f'b{L}'] = dw + 2 * self.reg * self.params[f'W{L}'], db 
        if self.batchnorm:
          for layer in range(1,L)[::-1]:
            if layer - 1 in max_pools: dout, dw, db, dgamma, dbeta = Conv_BatchNorm_ReLU_Pool.backward(dout,cache_dict[layer])
            else: dout, dw, db, dgamma, dbeta = Conv_BatchNorm_ReLU.backward(dout,cache_dict[layer])
            grads[f'W{layer}'], grads[f'b{layer}'] = dw + 2 * self.reg * self.params[f'W{layer}'], db
            grads[f'gamma{layer}'], grads[f'beta{layer}'] = dgamma, dbeta
        else:
          for layer in range(1,L)[::-1]:
            if layer - 1 in max_pools: dout, dw, db = Conv_ReLU_Pool.backward(dout,cache_dict[layer])
            else: dout, dw, db = Conv_ReLU.backward(dout,cache_dict[layer])
            grads[f'W{layer}'], grads[f'b{layer}'] = dw + 2 * self.reg * self.params[f'W{layer}'], db

        return loss, grads


def find_overfit_parameters():
    weight_scale = 2e-3   # Experiment with this!
    learning_rate = 1e-5  
    return weight_scale, learning_rate


def create_convolutional_solver_instance(data_dict, dtype, device):
    model = None
    solver = None
    input_dims = data_dict['X_train'].shape[1:]
    weight_scale = 'kaiming'
    num_classes = 10
    num_filters = ([32] * 2) + ([64] * 2) + ([128] * 1)
    max_pools = [1, 3, 4]
    reg_strength = 1e-5
    dtype = torch.float32
    device = 'cuda'
    model = DeepConvNet(input_dims=input_dims, num_classes=num_classes,
                    num_filters=num_filters, max_pools=max_pools,
                    weight_scale=weight_scale, reg=reg_strength,
                    dtype=dtype, device=device)
    solver = Solver(model, data_dict,
                num_epochs=100, batch_size=128,
                update_rule=adam,
                optim_config={'learning_rate': 0.002},
                print_every=50, device=device)
    return solver


def kaiming_initializer(Din, Dout, K=None, relu=True, device='cpu',
                        dtype=torch.float32):
    """
    Implement Kaiming initialization for linear and convolution layers.

    Inputs:
    - Din, Dout: Integers giving the number of input and output dimensions
      for this layer
    - K: If K is None, then initialize weights for a linear layer with
      Din input dimensions and Dout output dimensions. Otherwise if K is
      a nonnegative integer then initialize the weights for a convolution
      layer with Din input channels, Dout output channels, and a kernel size
      of KxK.
    - relu: If ReLU=True, then initialize weights with a gain of 2 to
      account for a ReLU nonlinearity (Kaiming initializaiton); otherwise
      initialize weights with a gain of 1 (Xavier initialization).
    - device, dtype: The device and datatype for the output tensor.

    Returns:
    - weight: A torch Tensor giving initialized weights for this layer.
      For a linear layer it should have shape (Din, Dout); for a
      convolution layer it should have shape (Dout, Din, K, K).
    """
    gain = 2. if relu else 1.
    weight = None
    if K is None:
        std = torch.sqrt(gain / torch.tensor(Din))
        weight = torch.randn(Din,Dout,dtype=dtype,device=device) * std
    else:
        ga = gain / torch.tensor(K*K*Din)
        std = torch.sqrt(ga)
        
        weight = torch.randn(Din,Dout,K,K,dtype=dtype,device=device) * std
    return weight


class BatchNorm(object):

    @staticmethod
    def forward(x, gamma, beta, bn_param):
        """
        Forward pass for batch normalization.

        During training the sample mean and (uncorrected) sample variance
        are computed from minibatch statistics and used to normalize the
        incoming data. During training we also keep an exponentially decaying
        running mean of the mean and variance of each feature, and these
        averages are used to normalize data at test-time.

        At each timestep we update the running averages for mean and
        variance using an exponential decay based on the momentum parameter:

        running_mean = momentum * running_mean + (1 - momentum) * sample_mean
        running_var = momentum * running_var + (1 - momentum) * sample_var

        Note that the batch normalization paper suggests a different
        test-time behavior: they compute sample mean and variance for
        each feature using a large number of training images rather than
        using a running average. For this implementation we have chosen to use
        running averages instead since they do not require an additional
        estimation step; the PyTorch implementation of batch normalization
        also uses running averages.

        Input:
        - x: Data of shape (N, D)
        - gamma: Scale parameter of shape (D,)
        - beta: Shift paremeter of shape (D,)
        - bn_param: Dictionary with the following keys:
          - mode: 'train' or 'test'; required
          - eps: Constant for numeric stability
          - momentum: Constant for running mean / variance.
          - running_mean: Array of shape (D,) giving running mean
            of features
          - running_var Array of shape (D,) giving running variance
            of features

        Returns a tuple of:
        - out: of shape (N, D)
        - cache: A tuple of values needed in the backward pass
        """
        mode = bn_param['mode']
        eps = bn_param.get('eps', 1e-5)
        momentum = bn_param.get('momentum', 0.9)

        N, D = x.shape
        running_mean = bn_param.get('running_mean',
                                    torch.zeros(D,
                                                dtype=x.dtype,
                                                device=x.device))
        running_var = bn_param.get('running_var',
                                   torch.zeros(D,
                                               dtype=x.dtype,
                                               device=x.device))

        out, cache = None, None
        if mode == 'train':
            ##################################################################
            # TODO: Implement the training-time forward pass for batch norm. #
            # Use minibatch statistics to compute the mean and variance, use #
            # these statistics to normalize the incoming data, and scale and #
            # shift the normalized data using gamma and beta.                #
            #                                                                #
            # You should store the output in the variable out.               #
            # Any intermediates that you need for the backward pass should   #
            # be stored in the cache variable.                               #
            #                                                                #
            # You should also use your computed sample mean and variance     #
            # together with the momentum variable to update the running mean #
            # and running variance, storing your result in the running_mean  #
            # and running_var variables.                                     #
            #                                                                #
            # Note that though you should be keeping track of the running    #
            # variance, you should normalize the data based on the standard  #
            # deviation (square root of variance) instead!                   #
            # Referencing the original paper                                 #
            # (https://arxiv.org/abs/1502.03167) might prove to be helpful.  #
            ##################################################################
            # Replace "pass" statement with your code
            mean = 1./N * x.sum(dim = 0)
            a = ((x - mean) ** 2).sum(dim = 0)
            va = 1./N * a
            running_mean = momentum * running_mean + (1 - momentum) * mean
            running_var = momentum * running_var + (1 - momentum) * va
            sqt = (va + eps).sqrt()
            rsqt = 1. / sqt
            x_hat = (x - mean) * rsqt
            out = gamma * x_hat + beta
            cache = (x, x_hat, mean, va, gamma, rsqt, eps)
            ################################################################
            #                           END OF YOUR CODE                   #
            ################################################################
        elif mode == 'test':
            ################################################################
            # TODO: Implement the test-time forward pass for               #
            # batch normalization. Use the running mean and variance to    #
            # normalize the incoming data, then scale and shift the        #
            # normalized data using gamma and beta. Store the result       #
            # in the out variable.                                         #
            ################################################################
            # Replace "pass" statement with your code
            a = (x - running_mean) / (running_var + eps)
            out = gamma * (a.sqrt()) + beta
            ################################################################
            #                      END OF YOUR CODE                        #
            ################################################################
        else:
            raise ValueError('Invalid forward batchnorm mode "%s"' % mode)

        # Store the updated running means back into bn_param
        bn_param['running_mean'] = running_mean.detach()
        bn_param['running_var'] = running_var.detach()

        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Backward pass for batch normalization.

        For this implementation, you should write out a
        computation graph for batch normalization on paper and
        propagate gradients backward through intermediate nodes.

        Inputs:
        - dout: Upstream derivatives, of shape (N, D)
        - cache: Variable of intermediates from batchnorm_forward.

        Returns a tuple of:
        - dx: Gradient with respect to inputs x, of shape (N, D)
        - dgamma: Gradient with respect to scale parameter gamma,
          of shape (D,)
        - dbeta: Gradient with respect to shift parameter beta,
          of shape (D,)
        """
        dx, dgamma, dbeta = None, None, None
        #####################################################################
        # TODO: Implement the backward pass for batch normalization.        #
        # Store the results in the dx, dgamma, and dbeta variables.         #
        # Referencing the original paper (https://arxiv.org/abs/1502.03167) #
        # might prove to be helpful.                                        #
        # Don't forget to implement train and test mode separately.         #
        #####################################################################
        # Replace "pass" statement with your code
        x, x_hat, mean, var, gamma, rsqrt, eps = cache
        N, D = x.shape
        dx = torch.zeros_like(x)
        dsigma2 = torch.zeros([D], dtype=dout.dtype, device=dout.device)
        dmu = torch.zeros([D], dtype=dout.dtype, device=dout.device)
        dgamma = torch.sum(x_hat * dout, dim=0)
        dbeta = torch.sum(dout, dim=0)
        dx_hat = gamma * dout
        dsigma2 += 0.5 * ((var + eps) ** (-1.5)) * torch.sum(dx_hat * (mean - x), dim=0)
        dmu += -rsqrt * torch.sum(dx_hat, dim=0) + dsigma2 * (-2/N) * torch.sum(x - mean, dim=0)
        dx += dx_hat * rsqrt + dsigma2 * (2./N) * (x - mean) + 1./N * dmu
        #################################################################
        #                      END OF YOUR CODE                         #
        #################################################################

        return dx, dgamma, dbeta

    @staticmethod
    def backward_alt(dout, cache):
        """
        Alternative backward pass for batch normalization.
        For this implementation you should work out the derivatives
        for the batch normalizaton backward pass on paper and simplify
        as much as possible. You should be able to derive a simple expression
        for the backward pass. See the jupyter notebook for more hints.

        Note: This implementation should expect to receive the same
        cache variable as batchnorm_backward, but might not use all of
        the values in the cache.

        Inputs / outputs: Same as batchnorm_backward
        """
        dx, dgamma, dbeta = None, None, None
        ###################################################################
        # TODO: Implement the backward pass for batch normalization.      #
        # Store the results in the dx, dgamma, and dbeta variables.       #
        #                                                                 #
        # After computing the gradient with respect to the centered       #
        # inputs, you should be able to compute gradients with respect to #
        # the inputs in a single statement; our implementation fits on a  #
        # single 80-character line.                                       #
        ###################################################################
        # Replace "pass" statement with your code
        x, x_hat, mean, var, gamma, rsqrt, eps = cache
        N, D = x.shape
        dx_hat = gamma * dout 
        hat = N * dx_hat - dx_hat.sum(dim=0)
        hat2 = (dx_hat * x_hat).sum(dim=0)
        dx = 1./N * rsqrt * (hat - x_hat * hat2) 
        dgamma, dbeta = (x_hat * dout).sum(dim = 0), dout.sum(dim = 0)
        #################################################################
        #                        END OF YOUR CODE                       #
        #################################################################

        return dx, dgamma, dbeta


class SpatialBatchNorm(object):

    @staticmethod
    def forward(x, gamma, beta, bn_param):
        """
        Computes the forward pass for spatial batch normalization.

        Inputs:
        - x: Input data of shape (N, C, H, W)
        - gamma: Scale parameter, of shape (C,)
        - beta: Shift parameter, of shape (C,)
        - bn_param: Dictionary with the following keys:
          - mode: 'train' or 'test'; required
          - eps: Constant for numeric stability
          - momentum: Constant for running mean / variance. momentum=0
            means that old information is discarded completely at every
            time step, while momentum=1 means that new information is never
            incorporated. The default of momentum=0.9 should work well
            in most situations.
          - running_mean: Array of shape (C,) giving running mean of
            features
          - running_var Array of shape (C,) giving running variance
            of features

        Returns a tuple of:
        - out: Output data, of shape (N, C, H, W)
        - cache: Values needed for the backward pass
        """
        out, cache = None, None

        ################################################################
        # TODO: Implement the forward pass for spatial batch           #
        # normalization.                                               #
        #                                                              #
        # HINT: You can implement spatial batch normalization by       #
        # calling the vanilla version of batch normalization you       #
        # implemented above. Your implementation should be very short; #
        # ours is less than five lines.                                #
        ################################################################
        # Replace "pass" statement with your code
        N, C, H, W = x.shape
        a = x.reshape(-1, C)
        out, cache = BatchNorm.forward(a, gamma, beta, bn_param)  
        out = out.view(N,C,H,W)
        ################################################################
        #                       END OF YOUR CODE                       #
        ################################################################

        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Computes the backward pass for spatial batch normalization.
        Inputs:
        - dout: Upstream derivatives, of shape (N, C, H, W)
        - cache: Values from the forward pass
        Returns a tuple of:
        - dx: Gradient with respect to inputs, of shape (N, C, H, W)
        - dgamma: Gradient with respect to scale parameter, of shape (C,)
        - dbeta: Gradient with respect to shift parameter, of shape (C,)
        """
        dx, dgamma, dbeta = None, None, None

        #################################################################
        # TODO: Implement the backward pass for spatial batch           #
        # normalization.                                                #
        #                                                               #
        # HINT: You can implement spatial batch normalization by        #
        # calling the vanilla version of batch normalization you        #
        # implemented above. Your implementation should be very short;  #
        # ours is less than five lines.                                 #
        #################################################################
        # Replace "pass" statement with your code
        N, C, H, W = dout.shape
        a = dout.view(-1, C)
        dx, dgamma, dbeta = BatchNorm.backward_alt(a, cache)
        dx = dx.view(N,C,H,W)
        ##################################################################
        #                       END OF YOUR CODE                         #
        ##################################################################

        return dx, dgamma, dbeta

##################################################################
#           Fast Implementations and Sandwich Layers             #
##################################################################


class FastConv(object):

    @staticmethod
    def forward(x, w, b, conv_param):
        N, C, H, W = x.shape
        F, _, HH, WW = w.shape
        stride, pad = conv_param['stride'], conv_param['pad']
        layer = torch.nn.Conv2d(C, F, (HH, WW), stride=stride, padding=pad)
        layer.weight = torch.nn.Parameter(w)
        layer.bias = torch.nn.Parameter(b)
        tx = x.detach()
        tx.requires_grad = True
        out = layer(tx)
        cache = (x, w, b, conv_param, tx, out, layer)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        try:
            x, _, _, _, tx, out, layer = cache
            out.backward(dout)
            dx = tx.grad.detach()
            dw = layer.weight.grad.detach()
            db = layer.bias.grad.detach()
            layer.weight.grad = layer.bias.grad = None
        except RuntimeError:
            dx, dw, db = torch.zeros_like(tx), \
                         torch.zeros_like(layer.weight), \
                         torch.zeros_like(layer.bias)
        return dx, dw, db


class FastMaxPool(object):

    @staticmethod
    def forward(x, pool_param):
        N, C, H, W = x.shape
        pool_height, pool_width = \
            pool_param['pool_height'], pool_param['pool_width']
        stride = pool_param['stride']
        layer = torch.nn.MaxPool2d(kernel_size=(pool_height, pool_width),
                                   stride=stride)
        tx = x.detach()
        tx.requires_grad = True
        out = layer(tx)
        cache = (x, pool_param, tx, out, layer)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        try:
            x, _, tx, out, layer = cache
            out.backward(dout)
            dx = tx.grad.detach()
        except RuntimeError:
            dx = torch.zeros_like(tx)
        return dx


class Conv_ReLU(object):

    @staticmethod
    def forward(x, w, b, conv_param):
        """
        A convenience layer that performs a convolution
        followed by a ReLU.
        Inputs:
        - x: Input to the convolutional layer
        - w, b, conv_param: Weights and parameters for the
          convolutional layer
        Returns a tuple of:
        - out: Output from the ReLU
        - cache: Object to give to the backward pass
        """
        a, conv_cache = FastConv.forward(x, w, b, conv_param)
        out, relu_cache = ReLU.forward(a)
        cache = (conv_cache, relu_cache)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Backward pass for the conv-relu convenience layer.
        """
        conv_cache, relu_cache = cache
        da = ReLU.backward(dout, relu_cache)
        dx, dw, db = FastConv.backward(da, conv_cache)
        return dx, dw, db


class Conv_ReLU_Pool(object):

    @staticmethod
    def forward(x, w, b, conv_param, pool_param):
        """
        A convenience layer that performs a convolution,
        a ReLU, and a pool.
        Inputs:
        - x: Input to the convolutional layer
        - w, b, conv_param: Weights and parameters for
          the convolutional layer
        - pool_param: Parameters for the pooling layer
        Returns a tuple of:
        - out: Output from the pooling layer
        - cache: Object to give to the backward pass
        """
        a, conv_cache = FastConv.forward(x, w, b, conv_param)
        s, relu_cache = ReLU.forward(a)
        out, pool_cache = FastMaxPool.forward(s, pool_param)
        cache = (conv_cache, relu_cache, pool_cache)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Backward pass for the conv-relu-pool
        convenience layer
        """
        conv_cache, relu_cache, pool_cache = cache
        ds = FastMaxPool.backward(dout, pool_cache)
        da = ReLU.backward(ds, relu_cache)
        dx, dw, db = FastConv.backward(da, conv_cache)
        return dx, dw, db


class Linear_BatchNorm_ReLU(object):

    @staticmethod
    def forward(x, w, b, gamma, beta, bn_param):
        """
        Convenience layer that performs an linear transform,
        batch normalization, and ReLU.
        Inputs:
        - x: Array of shape (N, D1); input to the linear layer
        - w, b: Arrays of shape (D2, D2) and (D2,) giving the
          weight and bias for the linear transform.
        - gamma, beta: Arrays of shape (D2,) and (D2,) giving
          scale and shift parameters for batch normalization.
        - bn_param: Dictionary of parameters for batch
          normalization.
        Returns:
        - out: Output from ReLU, of shape (N, D2)
        - cache: Object to give to the backward pass.
        """
        a, fc_cache = Linear.forward(x, w, b)
        a_bn, bn_cache = BatchNorm.forward(a, gamma, beta, bn_param)
        out, relu_cache = ReLU.forward(a_bn)
        cache = (fc_cache, bn_cache, relu_cache)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        """
        Backward pass for the linear-batchnorm-relu
        convenience layer.
        """
        fc_cache, bn_cache, relu_cache = cache
        da_bn = ReLU.backward(dout, relu_cache)
        da, dgamma, dbeta = BatchNorm.backward(da_bn, bn_cache)
        dx, dw, db = Linear.backward(da, fc_cache)
        return dx, dw, db, dgamma, dbeta


class Conv_BatchNorm_ReLU(object):

    @staticmethod
    def forward(x, w, b, gamma, beta, conv_param, bn_param):
        a, conv_cache = FastConv.forward(x, w, b, conv_param)
        an, bn_cache = SpatialBatchNorm.forward(a, gamma,
                                                beta, bn_param)
        out, relu_cache = ReLU.forward(an)
        cache = (conv_cache, bn_cache, relu_cache)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        conv_cache, bn_cache, relu_cache = cache
        dan = ReLU.backward(dout, relu_cache)
        da, dgamma, dbeta = SpatialBatchNorm.backward(dan, bn_cache)
        dx, dw, db = FastConv.backward(da, conv_cache)
        return dx, dw, db, dgamma, dbeta


class Conv_BatchNorm_ReLU_Pool(object):

    @staticmethod
    def forward(x, w, b, gamma, beta, conv_param, bn_param, pool_param):
        a, conv_cache = FastConv.forward(x, w, b, conv_param)
        an, bn_cache = SpatialBatchNorm.forward(a, gamma, beta, bn_param)
        s, relu_cache = ReLU.forward(an)
        out, pool_cache = FastMaxPool.forward(s, pool_param)
        cache = (conv_cache, bn_cache, relu_cache, pool_cache)
        return out, cache

    @staticmethod
    def backward(dout, cache):
        conv_cache, bn_cache, relu_cache, pool_cache = cache
        ds = FastMaxPool.backward(dout, pool_cache)
        dan = ReLU.backward(ds, relu_cache)
        da, dgamma, dbeta = SpatialBatchNorm.backward(dan, bn_cache)
        dx, dw, db = FastConv.backward(da, conv_cache)
        return dx, dw, db, dgamma, dbeta

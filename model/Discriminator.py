import torch.nn as nn
from model.block import conv_block


class SubDiscriminator(nn.Module):
    def __init__(self, act_type='leakyrelu', num_conv_block=3):
        super(SubDiscriminator, self).__init__()

        block = []

        in_channels = 3
        out_channels = 64

        for _ in range(num_conv_block):
            block += conv_block(in_channels, out_channels, stride=1, act_type=act_type, pad_type=None,
                                norm_type='instancenorm')
            in_channels = out_channels
            block += conv_block(in_channels, out_channels, stride=2, act_type=act_type, n_padding=1)
            out_channels *= 2

        out_channels //= 2
        in_channels = out_channels

        self.feature_extraction = nn.Sequential(*block)

        self.classification = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(out_channels, 1, 1),
        )

    def forward(self, x):
        x = self.feature_extraction(x)
        x = self.classification(x)
        return x


class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.discriminator_a = SubDiscriminator()
        self.discriminator_b = SubDiscriminator()
        self.sigmoid = nn.Sigmoid()

    def forward(self, a, b):
        a = self.discriminator_a(a)
        b = self.discriminator_b(b)
        return self.sigmoid(a - b)

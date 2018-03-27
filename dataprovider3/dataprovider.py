import numpy as np

from .dataset import Dataset


class DataProvider(object):
    """DataProvider.

    Args:
        dsets (list of Dataset): Datasets.
        augs (Augment): Augment.
        p (list of float): sampling weights.
    """
    def __init__(self):
        self.datasets = list()
        self.augments = None
        self.p = None
        self.spec = None

    def add_dataset(self, dset):
        assert isinstance(dset, Dataset)
        self.datasets.append(dset)

    def set_augment(self, aug):
        self.augments = aug

    def set_spec(self, spec):
        assert all([k in self.datasets for k in spec])
        self.spec = dict(spec)

    def set_imgs(self, imgs):
        assert len(imgs) > 0
        assert all([i in self.datasets for i in imgs])
        self.imgs = list(imgs)

    def set_sampling_weights(self, p=None):
        if p is None:
            p = [d.num_samples() for d in self.datasets]
        p = np.asarray(p, dtype='float32')
        p = p/np.sum(p)
        assert len(p)==len(self.datasets)
        self.p = p

    def random_dataset(self):
        assert len(self.datasets) > 0
        if self.p is None:
            self.set_sampling_weights()
        idx = np.random.choice(len(self.datasets), size=1, p=self.p)
        return self.datasets[idx[0]]

    def random_sample(self):
        dset = self.random_dataset()
        while True:
            try:
                spec = dict(self.spec)
                imgs = list(self.imgs)
                if self.augments is not None:
                    spec = self.augments.prepare(spec, imgs=imgs)
                sample = dset(spec=spec)
                break
            except Dataset.OutOfRangeError:
                pass
            except:
                raise
        return sample

    def __call__(self):
        return self.random_sample()

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for i, k in enumerate(self.datasets):
            format_string += '\n'
            format_string += '    {0:.3f} : {1}'.format(self.p[i], k)
        format_string += '\n)'
        return format_string
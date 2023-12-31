import numpy as np
import matplotlib.pyplot as plt
from time import time
from sklearn.feature_extraction.image import extract_patches_2d
from sklearn.decomposition import MiniBatchDictionaryLearning
from sklearn.feature_extraction.image import reconstruct_from_patches_2d


def show_with_diff(image, reference, title):
    """Helper function to display denoising"""
    plt.figure(figsize=(5, 3.3))
    plt.subplot(1, 2, 1)
    plt.title("Image")
    plt.imshow(image, vmin=0, vmax=1, cmap=plt.cm.gray, interpolation="nearest")
    plt.xticks(())
    plt.yticks(())
    plt.subplot(1, 2, 2)
    difference = image - reference

    plt.title("Difference (norm: %.2f)" % np.sqrt(np.sum(difference**2)))
    plt.imshow(
        difference, vmin=-0.5, vmax=0.5, cmap=plt.cm.PuOr, interpolation="nearest"
    )
    plt.xticks(())
    plt.yticks(())
    plt.suptitle(title, size=16)
    plt.subplots_adjust(0.02, 0.02, 0.98, 0.79, 0.02, 0.2)


def dictionary_builder(psize, bsize, distorted):
    # Extract all reference patches from the left half of the image
    
    height, width = distorted.shape
    t0 = time()
    patch_size = (psize, psize)
    data = extract_patches_2d(distorted[:, : width // 2], patch_size)
    data = data.reshape(data.shape[0], -1)
    data -= np.mean(data, axis=0)
    data /= np.std(data, axis=0)
    #print(f"{data.shape[0]} patches extracted in %.2fs." % (time() - t0))
    
    t0 = time()
    dico = MiniBatchDictionaryLearning(
        # increase to 300 for higher quality results at the cost of slower
        # training times.
        n_components=2*bsize,
        batch_size=bsize,
        alpha=1.0,
        max_iter=10,
    )
    V = dico.fit(data).components_
    dt = time() - t0
    print(f"{dico.n_iter_} iterations / {dico.n_steps_} steps in {dt:.2f}.")

    plt.figure(figsize=(4.2, 4))
    for i, comp in enumerate(V[:100]):
        plt.subplot(10, 10, i + 1)
        plt.imshow(comp.reshape(patch_size), cmap=plt.cm.gray_r, interpolation="nearest")
        plt.xticks(())
        plt.yticks(())
    plt.suptitle(
        "Dictionary learned from face patches\n"
        + "Train time %.1fs on %d patches" % (dt, len(data)),
        fontsize=16,
    )
    plt.subplots_adjust(0.08, 0.02, 0.92, 0.85, 0.08, 0.23)
    plt.show()
    return dico, V
    
def raccoon_learner(dico, V, original, distorted, psize, natoms, method):
    
    patch_size = (psize, psize)
    height, width = distorted.shape
    t0 = time()
    data = extract_patches_2d(distorted[:, width // 2 :], patch_size)
    data = data.reshape(data.shape[0], -1)
    intercept = np.mean(data, axis=0)
    data -= intercept    
    
    if natoms == 1:
        dstr = str(natoms) + " atom"
    else:
        dstr = str(natoms) + " atoms"
    
    transform_algorithms = [
        (method + "\n" + dstr, method, {"transform_n_nonzero_coefs": natoms})
    ]

    reconstructions = {}
    for title, transform_algorithm, kwargs in transform_algorithms:
        print(title + "...")
        reconstructions[title] = original.copy()
        t0 = time()
        dico.set_params(transform_algorithm=transform_algorithm, **kwargs)
        code = dico.transform(data)
        patches = np.dot(code, V)

        patches += intercept
        patches = patches.reshape(len(data), *patch_size)
        if transform_algorithm == "threshold":
            patches -= patches.min()
            patches /= patches.max()
        reconstructions[title][:, width // 2 :] = reconstruct_from_patches_2d(
            patches, (height, width // 2)
        )
        dt = time() - t0
        #print("done in %.2fs." % dt)
        show_with_diff(reconstructions[title], original, title + " (time: %.1fs)" % dt)
    plt.show()